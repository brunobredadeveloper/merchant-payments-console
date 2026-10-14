# Merchant Payments Console

**Backend e painel web para estudar pagamentos idempotentes, estornos e conciliação.**

Projeto de **Bruno Breda · breda_dev**. Oferecer um backend local reproduzível para o Tap Terminal, incluindo autorização persistida antes de uma resposta atrasada.

**Plataforma:** Python 3.11+ · HTTP · SQLite · painel HTML  
**Estado:** implementação de portfólio em evolução; esteira aprovada na execução referenciada.

[Fluxos e demonstração](docs/fluxos.md) · [Engenharia](docs/engenharia.md) · [Builds e evidências](docs/evidencias.md) · [Portfólio completo](https://github.com/brunobredadeveloper/breda-park-wash/blob/main/docs/portfolio-breda-dev.md)

## O que você pode avaliar

- API HTTP e dashboard de operações, aprovados e estornos.
- Idempotência persistida em SQLite e transações com BEGIN IMMEDIATE.
- Resposta perdida simulada, consulta por chave e estorno integral idempotente.
- Deduplicação de eventos e preservação de estornos diante de eventos tardios.

## Experiência e navegação

Veja o [mapa das telas e o roteiro de avaliação](docs/fluxos.md). Esta revisão não adiciona capturas sem origem verificável; imagens conceituais não são apresentadas como telas do aplicativo.

## Fluxo principal

1. Execute python server.py e abra http://127.0.0.1:8080.
2. Crie uma cobrança aprovada e atualize a lista.
3. Reenvie a mesma chave pela API; confira o mesmo identificador.
4. Use lost_response e consulte o resultado pela chave original.
5. Estorne uma aprovação e repita a solicitação; o estorno não pode duplicar.

## Executar e validar

Python 3.11 ou superior. Sem dependências externas de runtime. Armazenamento local em payments.sqlite3, ignorado pelo Git.

```sh
python server.py
# Em outro terminal:
python -m unittest -v
```

[Abrir a execução verificada no GitHub Actions](https://github.com/brunobredadeveloper/merchant-payments-console/actions/runs/38166073285). A conclusão dessa execução é **success**; consulte os artefatos e a revisão de código em [evidências](docs/evidencias.md).

## Limites do produto

Laboratório local sem autenticação, TLS, multiempresa, adquirente ou cartões. Não exponha o serviço à internet. Não gera APK ou IPA. O navegador do painel não foi validado visualmente nesta rodada.

## Para quem revisa o portfólio

Equipes que querem demonstrar o contrato entre aplicativo mobile e um serviço de pagamentos simulado. As [decisões de engenharia](docs/engenharia.md) conectam responsabilidades, arquivos e testes. O [roteiro funcional](docs/fluxos.md) ajuda a avaliar comportamento, falhas e preservação de dados. Funcionalidade planejada não é apresentada como implementada.

## Próximos passos

- Validar os percursos no dispositivo real e registrar os resultados.
- Revisar acessibilidade, interrupções e falhas de armazenamento/rede aplicáveis.
- Concluir requisitos de distribuição, suporte e segurança antes de uso comercial.

Código, mídias e dependências mantêm seus respectivos termos. Consulte os créditos e os avisos existentes no repositório.
