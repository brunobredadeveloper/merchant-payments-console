# Engenharia — Merchant Payments Console

## Problema técnico

Oferecer um backend local reproduzível para o Tap Terminal, incluindo autorização persistida antes de uma resposta atrasada.

## Responsabilidades e código

| Fronteira | Responsabilidade real | Onde inspecionar |
|---|---|---|
| Armazenamento | Store, SQLite e transações | [server.py](../server.py) |
| Contrato HTTP | Handler e validação de payload | [server.py](../server.py) |
| Interface | Dashboard HTML/JavaScript | [dashboard.html](../dashboard.html) |
| Testes | Concorrência, reinício e contrato HTTP | [test_server.py](../test_server.py) |

## Invariantes e decisões

- Mesma chave com valor ou cenário diferente retorna conflito HTTP 409.
- Evento de aprovação tardio não desfaz um estorno.
- Totais da tela são resumo do ledger, não fechamento contábil.

## Como examinar os testes

Os arquivos abaixo fazem parte do código versionado. A existência de uma suíte não comprova sua aprovação; o resultado remoto está em [evidências](evidencias.md).

- [test_server.py](../test_server.py)

## Limites e compromissos

Laboratório local sem autenticação, TLS, multiempresa, adquirente ou cartões. Não exponha o serviço à internet. Não gera APK ou IPA. O navegador do painel não foi validado visualmente nesta rodada.

A separação de responsabilidades documentada é a encontrada no código. Não se afirma certificação SOLID, paridade com produtos comerciais, auditoria de segurança ou operação em produção.

## Reproduzir a validação

```sh
python server.py
# Em outro terminal:
python -m unittest -v
```

[Voltar ao README](../README.md) · [Fluxos](fluxos.md)
