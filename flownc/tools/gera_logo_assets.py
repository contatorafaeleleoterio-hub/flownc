"""Gera os assets da logo a partir de docs/logo/logo FlowNC.jpeg.

Saidas (flownc/assets/logo/):
  - logo_flownc.png  — wordmark recortado, fundo transparente (TopBar).
  - flownc.ico       — icone multi-tamanho (janela + EXE).
Rodar uma vez (ou quando a logo mudar): python tools/gera_logo_assets.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
ORIGEM = RAIZ / "docs" / "logo" / "logo FlowNC.jpeg"
DESTINO = RAIZ / "flownc" / "assets" / "logo"


def main() -> None:
    img = Image.open(ORIGEM).convert("RGB")
    px = img.load()
    w, h = img.size

    # Fundo escuro vira transparencia: alpha proporcional ao brilho do pixel.
    out = Image.new("RGBA", (w, h))
    po = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            lum = max(r, g, b)
            a = 0 if lum < 36 else min(255, int((lum - 36) * 255 / 180))
            if a > 0:
                f = 255 / max(lum, 1)
                po[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
            else:
                po[x, y] = (0, 0, 0, 0)

    caixa = out.getbbox()
    recorte = out.crop(caixa)

    DESTINO.mkdir(parents=True, exist_ok=True)

    # PNG do wordmark (altura 96, proporcional) para a TopBar.
    alvo_h = 96
    alvo_w = round(recorte.width * alvo_h / recorte.height)
    recorte.resize((alvo_w, alvo_h), Image.LANCZOS).save(DESTINO / "logo_flownc.png")

    # ICO: quadrado com o fundo original da arte e o wordmark centralizado.
    fundo = px[4, 4]
    lado = max(recorte.size) + 80
    quad = Image.new("RGBA", (lado, lado), (*fundo, 255))
    quad.alpha_composite(recorte, ((lado - recorte.width) // 2, (lado - recorte.height) // 2))
    quad.resize((256, 256), Image.LANCZOS).save(
        DESTINO / "flownc.ico", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    )
    print(f"OK: {DESTINO / 'logo_flownc.png'} ({alvo_w}x{alvo_h}) e {DESTINO / 'flownc.ico'}")


if __name__ == "__main__":
    main()
