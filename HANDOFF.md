# Handoff — FlowNC — 2026-06-07
Status: redesign visual em andamento (Mudanças A e B implementadas; C a propor)

Feito nesta sessão:
- Investigado o problema "app abre pelado": confirmado NÃO resolvido — sem `core/seed.py`/`ensure_seed`, sem biblioteca Fanuc, sem perfil `FANUC_PADRAO` (só `MAZAK_VTC530` exemplo).
- `PLAN.md`: adicionado item 9 (Seed Fanuc) atômico — 9a defaults em `flownc/data_default/`, 9b `ensure_seed` idempotente, 9c chamar no boot, 9d empacotar no EXE, 9e lista de códigos (Mestre fornece).
- Direção corrigida: verificações automáticas de perfil (`must_exist`/`must_not_exist`) e regras automáticas SAEM do escopo. Biblioteca = código + descrição curta, editável; fluxo origem→destino. Adicionado bloco "Como fica na nova atualização" no Objetivo, Glossário (Lógica atual) e Estado auditado.

Onde parou: `PLAN.md` atualizado com Seed Fanuc + escopo de verificações descartado.

Próximo passo: Mestre vai fornecer a lista de códigos da biblioteca Fanuc → preencher item 9e. Depois, propor a Mudança C via `/opsx:propose` (etapas 22+).

Blockers:
- Aguardando lista de códigos Fanuc do Mestre (item 9e).
- Lacunas de empacotamento abertas: `FlowNC.spec datas=[]`, fontes IBM Plex, seed (item 9).

Arquivos tocados: PLAN.md.

Retomar com: "continuar"
