# Runbook — Falta Memoria

## Objetivo

Orientar diagnóstico somente leitura para `Falta Memoria`.

## Sintomas

Alertas, eventos Warning, condições degradadas, indisponibilidade ou aumento de erros.

## Impacto

Descreva impacto técnico e de negócio conforme evidências.

## Pré-requisitos

`oc` autenticado, permissões somente leitura, contexto e ambiente validados.

## Verificações iniciais

```bash
scripts/preflight.sh
scripts/resumo-saude.sh
```

## Evidências esperadas

Condições e mensagens, eventos recentes, logs limitados quando aplicável e relação temporal entre sintomas.

## Causas comuns

Capacidade insuficiente, dependência indisponível, configuração externa incorreta, rollout incompleto, falha de imagem, scheduling, storage, rede ou certificado.

## Critérios de escalonamento

Impacto em produção, API/etcd/authentication/ingress/storage indisponíveis ou falta de evidência suficiente.

## Dados para suporte Red Hat

Manifesto de evidências, must-gather sanitizado quando aprovado, timeline, versões e operadores afetados.

## Plano de remediação proposto

Documentar ações recomendadas sem executá-las pelo toolkit.

## Validação pós-correção

Executar nova coleta e comparar com a coleta anterior.
