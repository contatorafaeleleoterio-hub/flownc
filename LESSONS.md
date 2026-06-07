# Lessons — FlowNC

## 2026-06-07 — Não inferir direção a partir de arquivo de exemplo
O preset `MAZAK_VTC530.json` tem `global_rules`/`verifications` por ser exemplo antigo. Isso NÃO reflete o sistema definido no plano: verificações automáticas e regras de perfil foram **retiradas do escopo**. A biblioteca é só código + descrição editável (operador monta a troca manualmente, origem→destino). Antes de propor conteúdo de perfil/biblioteca, conferir a direção no `PLAN.md` — não copiar do exemplo. Quando algo antigo não reflete mais o plano, descartar e marcar "como fica na nova atualização" no próprio plano, para o próximo agente não reler nem perguntar.

## 2026-06-07 — Biblioteca tem `replace` vazio de propósito (NÃO preencher)
A biblioteca (`data/library.json` e `data_default/library.json`, 89 códigos) usa schema `find`=código, `replace`=**vazio**, `label`=descrição, `tags`=categoria. O `replace` vazio é **intencional**: a biblioteca é um **dicionário de códigos** (código + significado), não uma lista de trocas prontas; o destino quem escolhe é o operador, na tela de montar edição.
- **Risco transitório:** enquanto o Compositor não for reescrito (Próximo passo 1), a tela antiga espera um par "de → para" e pode tratar um código da biblioteca como "trocar por nada" (apagar). Até a reescrita, não usar os códigos da biblioteca direto na tela antiga.
- **NÃO "consertar" preenchendo o `replace`** — isso volta ao modelo de pares prontos, que foi **descartado**. A correção certa é a tela nova com **dois campos** (código que sai / código que entra).
- **3 perfis iniciais:** `MAQ01`/`MAQ02`/`MAQ03` (só esses; sem regras nem verificações). Exemplo `MAZAK_VTC530.json` removido (git preserva).
