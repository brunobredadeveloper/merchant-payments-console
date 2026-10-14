# Validação do backend

Em 14/10/2026, a suíte `python -m unittest -v` foi executada novamente na revisão documental. São 11 testes: persistência após reinício, concorrência, conflito de payload, limites de valores, estorno/replay, recusa de estorno inválido, deduplicação/conflito de evento, evento tardio, estado de resposta perdida e contrato HTTP com timeout/consulta.

O estado remoto da esteira está em [evidências](evidencias.md). A aparência do painel no navegador não foi validada visualmente nesta rodada. Teste de API não equivale a auditoria de segurança ou implantação em produção.
