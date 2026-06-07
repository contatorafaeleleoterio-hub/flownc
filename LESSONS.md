# Lessons — FlowNC

## 2026-06-07 — Não inferir direção a partir de arquivo de exemplo
O preset `MAZAK_VTC530.json` tem `global_rules`/`verifications` por ser exemplo antigo. Isso NÃO reflete o sistema definido no plano: verificações automáticas e regras de perfil foram **retiradas do escopo**. A biblioteca é só código + descrição editável (operador monta a troca manualmente, origem→destino). Antes de propor conteúdo de perfil/biblioteca, conferir a direção no `PLAN.md` — não copiar do exemplo. Quando algo antigo não reflete mais o plano, descartar e marcar "como fica na nova atualização" no próprio plano, para o próximo agente não reler nem perguntar.

## 2026-06-07 — Biblioteca tem `replace` vazio de propósito (NÃO preencher)
A biblioteca (`data/library.json` e `data_default/library.json`, 89 códigos) usa schema `find`=código, `replace`=**vazio**, `label`=descrição, `tags`=categoria. O `replace` vazio é **intencional**: a biblioteca é um **dicionário de códigos** (código + significado), não uma lista de trocas prontas; o destino quem escolhe é o operador, na tela de montar edição.
- **Risco transitório:** enquanto o Compositor não for reescrito (Próximo passo 1), a tela antiga espera um par "de → para" e pode tratar um código da biblioteca como "trocar por nada" (apagar). Até a reescrita, não usar os códigos da biblioteca direto na tela antiga.
- **NÃO "consertar" preenchendo o `replace`** — isso volta ao modelo de pares prontos, que foi **descartado**. A correção certa é a tela nova com **dois campos** (código que sai / código que entra).
- **3 perfis iniciais:** `MAQ01`/`MAQ02`/`MAQ03` (só esses; sem regras nem verificações). Exemplo `MAZAK_VTC530.json` removido (git preserva).

## 2026-06-07 — Design é contrato: protótipo HTML antes do código (Regra de Ouro)
Causa raiz das entregas que saíam visualmente diferentes do proposto: o design era improvisado durante a programação. Decisão do Mestre: **separar a decisão visual da construção**. Fase 1 = protótipo HTML completo e interativo (TODAS as telas e popups do inventário), offline, aprovado pelo Mestre ("é esse") — vira o **contrato visual congelado**. Só depois: Fase 2 = app nativo (PySide6) reproduzindo o protótipo à risca, tela por tela com conferência lado a lado; Fase 3 = ligar backend sem tocar no layout aprovado.
- **Regra prática:** nenhuma tela/popup nasce no código sem antes existir e estar aprovada no protótipo. Mudança visual = primeiro o protótipo + nova aprovação, depois o código.
- **Tecnologia:** protótipo em HTML/CSS/JS; produção em PySide6 nativo (o HTML NÃO roda dentro do app — é só referência). Mantém EXE pequeno, sem navegador embutido.
- Registrado no topo do `PLAN.md` (Regra de Ouro + Reestruturação em 3 fases). Próximos passos 1–6 → Fase 2; 4/7/8/9 + Mudanças C/D → Fase 3.

## 2026-06-07 — Auditoria de terceiro também erra: verificar cada afirmação no código real
Uma auditoria do "sênior" (`auditoria_plano.md`) apontou 3 "erros críticos"; só 1 era real. Conferindo arquivo por arquivo: **CRLF no `publisher.py`** = alarme falso (ele é **byte-exato**, `read_bytes`/`_write_bytes_atomic`, não usa `read_text`/`write_text`); **`scope-select` faltando** = alarme falso (não existe no mockup v2, 0 ocorrências); **`verifier.py` não existe** = errado (existe). Real mesmo: só `data_default/` fora do `datas` do `.spec`. As classes de overlay citadas (`diff-line`/`summary-grid`/…) eram fictícias — as reais são `.run`/`.res`/`.confirm`/`.saved`.
- **Regra prática:** antes de agir sobre qualquer auditoria/relatório externo, validar cada item lendo o código real (nome de função > número de linha, que sofre drift). Registrar o veredito por escrito no `PLAN.md` ("Resposta à auditoria") para não reabrir a discussão.
