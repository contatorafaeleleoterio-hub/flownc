# Lessons — FlowNC

## 2026-06-07 — Não inferir direção a partir de arquivo de exemplo
O preset `MAZAK_VTC530.json` tem `global_rules`/`verifications` por ser exemplo antigo. Isso NÃO reflete o sistema definido no plano: verificações automáticas e regras de perfil foram **retiradas do escopo**. A biblioteca é só código + descrição editável (operador monta a troca manualmente, origem→destino). Antes de propor conteúdo de perfil/biblioteca, conferir a direção no `PLAN.md` — não copiar do exemplo. Quando algo antigo não reflete mais o plano, descartar e marcar "como fica na nova atualização" no próprio plano, para o próximo agente não reler nem perguntar.
