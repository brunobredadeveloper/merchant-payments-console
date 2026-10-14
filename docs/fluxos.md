# Fluxos de uso — Merchant Payments Console

Oferecer um backend local reproduzível para o Tap Terminal, incluindo autorização persistida antes de uma resposta atrasada.

## Mapa de telas

| Tela / área | O que a pessoa faz | Referência de implementação |
|---|---|---|
| Painel web | Consultar totais do ledger local. | [dashboard.html](../dashboard.html) |
| Nova cobrança | Informar valor e cenário fictício. | [dashboard.html](../dashboard.html) |
| Operações | Listar identificador, valor e resultado. | [server.py](../server.py) |
| Estornar | Solicitar estorno integral de uma aprovação. | [server.py](../server.py) |
| Repetir evento | Verificar deduplicação do evento simulado. | [server.py](../server.py) |

## Demonstração guiada

Use dados fictícios, em ambiente de avaliação.

1. Execute python server.py e abra http://127.0.0.1:8080.
2. Crie uma cobrança aprovada e atualize a lista.
3. Reenvie a mesma chave pela API; confira o mesmo identificador.
4. Use lost_response e consulte o resultado pela chave original.
5. Estorne uma aprovação e repita a solicitação; o estorno não pode duplicar.

## Casos que merecem atenção

- Mesma chave com valor ou cenário diferente retorna conflito HTTP 409.
- Evento de aprovação tardio não desfaz um estorno.
- Totais da tela são resumo do ledger, não fechamento contábil.

## Escopo e resultado esperado

Laboratório local sem autenticação, TLS, multiempresa, adquirente ou cartões. Não exponha o serviço à internet. Não gera APK ou IPA. O navegador do painel não foi validado visualmente nesta rodada.

## Checklist para validação do proprietário

- [ ] Instalar/abrir a versão correspondente às evidências.
- [ ] Percorrer a jornada principal e uma condição de falha.
- [ ] Confirmar navegação, retorno, teclado e leitura em tela pequena.
- [ ] Fechar/reabrir e verificar os dados que devem persistir.
- [ ] Avaliar os recursos nativos pertinentes no aparelho real.
- [ ] Registrar versão, aparelho, resultado esperado e observado em eventual relato.

[Voltar ao README](../README.md) · [Evidências](evidencias.md)
