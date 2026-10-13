# Grupo:Ana Carolina Ramos, Anna Carolina Souza,Breno Henrique Barcelos, Caio Leonardo, Cauã Monteiro, João Pedro Penha Lourenço
# Refactor Race Python

Processamento de pedidos com descontos por cliente e cupom, frete, impostos,
pontos de fidelidade e identificação de produtos repetidos.

## Executar no Windows

Requer Python 3.10 ou superior. No terminal PowerShell, dentro da pasta:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pytest --cov=src.legacy_checkout --cov-branch --cov-report=term-missing
```

Não é necessário instalar plugin separado para pytest. No VS Code, a extensão
Python permite usar a aba de testes. Abra esta pasta, selecione o interpretador
.venv/Scripts/python.exe e atualize a descoberta de testes.
O arquivo .vscode/settings.json habilita o pytest.

## Diagnóstico inicial e code smells

- A refatoração parcial recebida não propagava o desconto do cupom ao resultado.
  O teste test_coupon já falhava antes desta intervenção.
- A detecção de duplicados usava dois laços aninhados, com custo quadrático.
- Taxas, limites e valores de frete estavam espalhados em números literais.
- A seleção de imposto repetia condicionais para cada estado.
- Cálculo, impressão e armazenamento ainda compartilhavam a função principal.
- O histórico global dificultava o isolamento dos testes.

## Refatorações realizadas

- Constantes nomeadas centralizam taxas, limites, cupons, frete e pontos.
- TAX_RATES substitui os condicionais de imposto.
- calc_desconto_total concentra a aplicação do cupom e do limite de 25%.
  O resultado é utilizado no total e no campo discount.
- Counter substitui a busca quadrática. A ordem dos nomes duplicados
  continua sendo a da primeira ocorrência.
- _calcula_valores faz os cálculos sem efeitos colaterais.
  _formata_resultado cuida do arredondamento e _imprime_resumo da saída.
- calcula_pedido permite consultar o resultado sem imprimir nem armazenar.
  process_order preserva a interface pública e o histórico do legado.
- Uma fixture isola o histórico entre os testes.

## Testes adicionados

Foram acrescentados 40 casos aos quatro testes existentes:
limiares de descontos de clientes, funcionário, tipo desconhecido,
todos os cupons, limite de 25%, sensibilidade a maiúsculas,
impostos dos quatro estados regionais e de outro estado, frete expresso,
ordem dos duplicados, pedido vazio, quantidades não positivas,
pontos antes do arredondamento, saída no console, histórico e ausência
de alteração das entradas.

Resultado final: 44 casos aprovados, 100% de cobertura de linhas e ramificações.
Veja METRICS.md e os arquivos de evidência em reports/.

## Decisões técnicas

As regras de negócio do código original foram preservadas, incluindo frete
grátis baseado no subtotal antes do desconto, imposto sem frete, pontos
calculados antes do arredondamento e cupons sensíveis a maiúsculas.
Quantidades não positivas continuam com o comportamento legado.
Os exemplos de requisitos futuros do material não foram ativados.

As funções auxiliares da versão recebida foram mantidas, incluindo
calc_valor_com_desconto. Os testes recebidos não tiveram suas expectativas
alteradas. O arquivo BASELINE - NÃO ALTERAR também foi preservado.

Os cálculos continuam usando float para preservar o arredondamento existente.
A saída monetária é arredondada somente ao formatar o resultado.
As mensagens no console conservam os valores brutos do legado.

## Uso de inteligência artificial

Ferramenta utilizada: OpenAI Codex.
Finalidade: análise do código, refatoração, correção da regressão de cupom,
ampliação dos testes e execução das verificações.
Exemplo: uso de Counter para contar duplicados mantendo a ordem original.
Validação executada pelo agente: suíte pytest, cobertura de ramificações,
Ruff, Radon e comparação de 2.000 entradas com o código original do Git.
A revisão humana da solução ainda cabe ao responsável pelo projeto.

## Melhorias futuras e limitações

- O histórico global permanece por compatibilidade; armazenamento injetável
  seria uma evolução futura da API.
- Validação de entradas, Decimal e normalização de cupons exigem novos
  requisitos porque podem alterar o comportamento atual.
- A equipe deve preencher seus integrantes e cuidar da entrega acadêmica.
- Não foi feita publicação no GitHub nem criado histórico artificial de commits.
