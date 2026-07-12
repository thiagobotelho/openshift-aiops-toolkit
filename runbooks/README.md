# Runbooks

Esta pasta contém runbooks de triagem para sintomas comuns em OpenShift.

Runbook não é automação. Ele é um roteiro humano para decidir quais evidências coletar, qual impacto avaliar e quando escalar.

## Estado atual

Os runbooks estão prontos como base operacional de triagem.

Eles seguem uma estrutura comum:

- objetivo;
- sintomas;
- impacto;
- pré-requisitos;
- verificações iniciais;
- evidências esperadas;
- causas comuns;
- critérios de escalonamento;
- dados para suporte;
- plano proposto;
- validação pós-correção.

Alguns runbooks ainda são propositalmente genéricos. A expectativa é especializar com comandos, consultas e critérios próprios conforme incidentes reais forem acontecendo.

## Como escolher

| Sintoma | Runbook sugerido |
| --- | --- |
| Pod reiniciando | `pod-crashloopbackoff.md` |
| Pod não agenda | `pod-pending.md` |
| Falha de pull de imagem | `pod-imagepullbackoff.md` |
| Node indisponível | `node-notready.md` |
| Storage pendente | `pvc-pending.md` |
| Operador degradado | `clusteroperator-degraded.md` |
| Autenticação degradada | `authentication-degradado.md` |
| DNS indisponível | `dns-indisponivel.md` |
| Ingress/Route com erro | `ingress-degradado.md` ou `route-indisponivel.md` |
| OLM travado | `olm-installplan-pendente.md` |

## Fluxo recomendado

1. Execute a coleta completa segura.
2. Identifique o sintoma principal.
3. Abra o runbook correspondente.
4. Execute apenas diagnósticos direcionados necessários.
5. Registre achados usando `templates/achado.md`.
6. Proponha remediação fora do toolkit.
