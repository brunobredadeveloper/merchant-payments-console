# Contrato HTTP e execução local

Python 3.11+, sem dependências externas de runtime.

```sh
python server.py
python -m unittest -v
```

Abra http://127.0.0.1:8080. SQLite persiste em `payments.sqlite3`, ignorado pelo Git. `PAYMENTS_DB`, `HOST` e `PORT` alteram os padrões. O bind é loopback; não exponha o serviço sem autenticação e proteção apropriadas.

Emulador Android: `http://10.0.2.2:8080`. Aparelho USB: execute `adb reverse tcp:8080 tcp:8080` e use `http://127.0.0.1:8080` no app.

| Método | Rota | Contrato |
|---|---|---|
| POST | `/api/payments` | `idempotencyKey`, `amountInCents`, `scenario` |
| GET | `/api/payments/by-key/{key}` | Consultar resultado persistido |
| GET | `/api/payments` | Listar ledger |
| POST | `/api/payments/{id}/refund` | Estorno integral idempotente simulado |
| POST | `/api/events` | `eventId`, `paymentId`, `kind`; deduplicação |
| GET | `/health` | Saúde do serviço |

Valores BRL em centavos inteiros, positivos, até R$ 1.000.000. Cenários: `approve`, `decline`, `lost_response`. Primeira criação: HTTP 201. Replay exato: HTTP 200 e mesmo pagamento. Chave com payload diferente: HTTP 409.

```sh
curl -H 'Content-Type: application/json' \
  -d '{"idempotencyKey":"demo-001","amountInCents":2590,"scenario":"approve"}' \
  http://127.0.0.1:8080/api/payments
```

`lost_response` persiste a aprovação e atrasa a primeira resposta por cinco segundos. O cliente Android usa timeout de dois segundos; consulta posterior pela mesma chave encontra a aprovação. Replay idêntico não cria cobrança nem repete o atraso.

`BEGIN IMMEDIATE`, chaves únicas e transações protegem concorrência e eventos associados. IDs de eventos com payload conflitante são rejeitados. Evento tardio não desfaz estorno. Painel resume ledger ao vivo; não é fechamento fiscal/contábil. Não há webhook externo conectado, estorno parcial ou múltiplos lojistas.

<!-- RELOCATED_LINKS: referência realocada de README.md para docs/ -->
