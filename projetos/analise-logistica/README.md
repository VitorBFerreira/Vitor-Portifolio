# 📦 Análise Logística com Python

**Projeto público demonstrativo** de automação e análise de abastecimento, desenvolvido para mostrar habilidades de Python, tratamento de dados e regras de negócio.

> **Privacidade:** esta implementação foi criada para portfólio e funciona exclusivamente com dados fictícios. Não integra sistemas corporativos, não reproduz planilhas internas e não corresponde a uma implantação produtiva.

## O problema
Conferir estoques, reservas e múltiplos manualmente pode gerar retrabalho. O projeto ilustra como organizar essas informações e gerar uma recomendação de reposição auditável.

## O que a demonstração faz
- Lê três arquivos CSV: estoques, reservas e múltiplos.
- Soma as necessidades e os atendimentos por material antes de calcular o saldo pendente.
- Deduz o estoque comprometido uma única vez do estoque de origem.
- Arredonda faltas para cima, respeitando pallets completos.
- Limita as recomendações ao estoque disponível no destino.
- Identifica múltiplos inconsistentes, materiais sem cobertura e reservas com atendimento maior que o necessário.
- Exporta um relatório CSV para abertura no Excel.

## Como executar
Requisito: **Python 3.10+**. Não depende de bibliotecas externas.

```bash
python analise_logistica.py
```

O arquivo `relatorio.csv` será criado na pasta deste projeto. Para informar outros arquivos, use:

```bash
python analise_logistica.py --dados ./exemplos --saida ./resultado.csv
```

Para conferir as regras:
```bash
python -m unittest discover -s testes -v
```

## Estrutura
```text
analise_logistica.py
exemplos/
  estoques.csv
  reservas.csv
  multiplos.csv
testes/
  test_analise.py
```

## Principais regras
- Demanda líquida: `max(soma(necessario) - soma(atendido), 0)`
- Estoque útil: `max(estoque_origem - estoque_comprometido, 0)`
- Pallets necessários: `ceil(max(demanda_liquida - estoque_util, 0) / kg_por_pallet)`
- Sugestão: mínimo entre pallets necessários e pallets completos disponíveis no estoque destino.
- Múltiplos ausentes ou divergentes: pedido automático bloqueado.

### Limites desta demonstração
A versão pública não possui integração SAP, movimentações de transporte, regras de calendário ou gestão de caminhões. Não é indicada para decisões operacionais sem validação humana e sem integração a dados confiáveis.

**Tecnologias:** Python, CSV, testes automatizados com unittest.
