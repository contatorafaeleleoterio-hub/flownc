"""CLI do CNC Batch Editor — protótipo executável da fatia vertical (PRD v2.3).

Fluxo (secao 11.3): carregar perfil -> ler arquivos -> dry-run com contagem e
preview -> verificacoes -> salvar em pasta separada (so com --salvar e sem
bloqueio, secao 11.7). Nunca altera os originais.

Uso:
    python cli.py <pasta> --preset <preset.json> [--salvar]
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

from core.file_handler import (
    BinaryFileError,
    list_input_files,
    make_output_dir,
    read_file,
    write_atomic,
)
from core.matcher import suggest_leading_zero_variant
from core.models import OnZeroMatches, Severity
from core.preset_store import PresetError, all_rules, load_preset
from core.replacement_plan import build_plan
from core.replacer import apply_edits
from core.session_log import SessionLog
from core.verifier import is_blocking, run_configurable, run_structural


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _diff_preview(original: str, result: str, limit: int = 12) -> list[str]:
    diff = difflib.unified_diff(
        original.splitlines(), result.splitlines(), lineterm="", n=1
    )
    body = [ln for ln in diff if ln and ln[0] in "+-" and not ln.startswith(("+++", "---"))]
    return body[:limit]


def processar(source_dir: Path, preset_path: Path, salvar: bool) -> int:
    log = SessionLog()
    try:
        preset = load_preset(preset_path)
    except PresetError as exc:
        print(f"ERRO: {exc}")
        return 2

    rules = all_rules(preset)
    files = list_input_files(source_dir, preset.extensions)
    print(f"Perfil: {preset.machine}  |  case_sensitive={preset.case_sensitive}")
    print(f"Pasta:  {source_dir}")
    print(f"Arquivos elegiveis: {len(files)}  (extensoes {preset.extensions})\n")
    log.add(f"Perfil {preset.machine}; {len(files)} arquivos")

    batch_counts: dict[str, int] = {r.id: 0 for r in rules}
    blocked = False
    results: list[tuple[Path, str, str, object]] = []  # (path, original, result, info)
    sample_text = ""

    for path in files:
        try:
            text, info = read_file(path)
        except BinaryFileError as exc:
            print(f"  [VERMELHO] {path.name}: {exc} — excluido do lote\n")
            log.add(f"{path.name}: erro de leitura, excluido")
            continue
        sample_text += text
        plan = build_plan(text, rules, preset.case_sensitive, current_file=path.name)
        result = apply_edits(text, plan.edits)
        for rid, n in plan.match_count_by_rule.items():
            batch_counts[rid] = batch_counts.get(rid, 0) + n

        structural = run_structural(text, result)
        config = run_configurable(result, preset.verifications, preset.case_sensitive)
        if is_blocking(structural):
            blocked = True

        print(f"  {path.name}  [{info.encoding}/{info.confidence}, EOL={info.eol!r}]"
              f"  edicoes={len(plan.edits)}")
        for e in plan.edits:
            print(f"      linha {_line_of(text, e.start):>4}: {e.matched!r} -> "
                  f"{e.replacement!r}  (regra {e.rule_id})")
        for s in plan.suppressions:
            print(f"      [AMARELO] conflito: regra {s.loser_rule_id} suprimida por "
                  f"{s.winner_rule_id} — {s.reason}")
        for vr in structural + config:
            cor = "VERMELHO" if vr.severity is Severity.CRITICAL else "AMARELO"
            print(f"      [{cor}] {vr.label}: {vr.message}")
        for ln in _diff_preview(text, result):
            print(f"        {ln}")
        print()
        results.append((path, text, result, info))
        log.add(f"{path.name}: {len(plan.edits)} edicoes, {len(structural+config)} alertas")

    # Regras sem ocorrencia no lote (secao 8.5) + dica de leading-zero.
    print("Regras ativas sem ocorrencia no lote:")
    any_zero = False
    for r in rules:
        if not r.active or r.on_zero_matches is OnZeroMatches.IGNORE:
            continue
        if batch_counts.get(r.id, 0) == 0:
            any_zero = True
            hint = suggest_leading_zero_variant(sample_text, r.find)
            sugestao = f"  Encontrado '{hint}' — voce quis dizer '{hint}'?" if hint else ""
            nivel = "VERMELHO/BLOQUEIA" if r.on_zero_matches is OnZeroMatches.ERROR else "AMARELO"
            print(f"  [{nivel}] regra {r.id} ('{r.find}'): 0 ocorrencias.{sugestao}")
            if r.on_zero_matches is OnZeroMatches.ERROR:
                blocked = True
    if not any_zero:
        print("  (nenhuma)")
    print()

    if not salvar:
        print("Dry-run concluido. Use --salvar para gravar (em pasta separada).")
        return 0

    if blocked:
        print("BLOQUEADO (secao 11.7): erro estrutural critico ou regra error com 0 "
              "ocorrencias. Nada foi salvo.")
        return 1
    if not results:
        print("Nada a salvar (todos os arquivos falharam na leitura).")
        return 1

    out_dir = make_output_dir(source_dir, preset.machine)
    for path, _orig, result, info in results:
        write_atomic(out_dir / path.name, result, info)
    log.add(f"Salvos {len(results)} arquivos em {out_dir.name}")
    log.export_txt(out_dir.parent / f"{out_dir.name}_log.txt")
    print(f"Salvo: {len(results)} arquivos em {out_dir}")
    print(f"Log:   {out_dir.name}_log.txt")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser(description="CNC Batch Editor (protótipo CLI)")
    parser.add_argument("pasta", type=Path, help="pasta com os arquivos NC")
    parser.add_argument("--preset", type=Path, required=True, help="arquivo de preset JSON")
    parser.add_argument("--salvar", action="store_true", help="grava o resultado")
    args = parser.parse_args(argv)
    if not args.pasta.is_dir():
        print(f"ERRO: pasta nao encontrada: {args.pasta}")
        return 2
    return processar(args.pasta, args.preset, args.salvar)


if __name__ == "__main__":
    raise SystemExit(main())
