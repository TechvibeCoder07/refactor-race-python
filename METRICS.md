# Métricas antes e depois

Medições reais de 10/10/2026, com Python 3.10.11, pytest 9.1.1,
pytest-cov 7.1.0, Radon 6.0.1 e Ruff 0.17.0.

A coluna Antes representa a pasta recebida, que já continha alterações locais
em relação ao Git. Não representa a versão monolítica original.

| Indicador | Antes | Depois |
| --- | ---: | ---: |
| Casos coletados pelo pytest | 4 | 44 |
| Casos aprovados | 3 | 44 |
| Casos com falha | 1 | 0 |
| Cobertura de linhas | 86,36% (76/88) | 100% (92/92) |
| Cobertura de ramificações | 72% (36/50) | 100% (18/18) |
| Cobertura combinada | 81,16% | 100% |
| Complexidade de process_order | 1 (A) | 1 (A) |
| Complexidade média | 4,11 (A) | 2,57 (A) |
| Maior complexidade por função | 7 (B) | 6 (B) |
| Índice de manutenibilidade | 31,9753 (A) | 31,9715 (A) |
| Problemas no módulo pelo Ruff, com as mesmas regras | 7 | 0 |
| Busca de duplicados | O(n²) | O(n) |

A complexidade média caiu cerca de 37,45%. A função principal já tinha sido
extraída na versão recebida e manteve complexidade 1. O índice de
manutenibilidade ficou praticamente estável, com pequena redução; portanto,
não houve melhora mensurável nesse indicador.

O teste de cupom falhava porque o desconto do cupom era aplicado ao total,
mas não era propagado ao campo discount e à mensagem de desconto.
A correção restaura o comportamento do código original registrado no Git.
Os quatro testes recebidos foram preservados.

Além do pytest, foram comparados 2.000 casos determinísticos com o código
original do commit a88772b. Resultados, mensagens e histórico coincidiram.
Essa amostra não prova equivalência para todas as entradas possíveis.

## Evidências

- reports/antes/: execução inicial, cobertura JSON, complexidade, Ruff,
  manutenibilidade e cópia do código recebido.
- reports/depois/: execução final e métricas.
- reports/original_git.py.txt: código original usado na comparação.
- reports/check_compatibility.py: comparação reproduzível.
- reports/compatibilidade.txt: resultado da comparação.

## Comandos de reprodução

Execute na raiz do projeto, usando o Python do ambiente virtual:

```powershell
python -m pytest -v --cov=src.legacy_checkout --cov-branch --cov-report=term-missing
python -m radon cc src/legacy_checkout.py -s -a
python -m radon mi src/legacy_checkout.py -s
python -m ruff check src tests
python reports/check_compatibility.py
```

O Ruff verifica E4, E7, E9, F, SIM e PLR1730, definidos em ruff.toml.
Na execução inicial, a configuração global herdada apontava quatro problemas.
A comparação com regras explícitas e idênticas aponta sete problemas antes
e zero depois; a saída adicional está em reports/antes/ruff_comparavel.txt.
Os caminhos das ferramentas foram adaptados à organização src/ e tests/.
