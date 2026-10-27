# Validação do toolkit

## Pré-requisitos

Python compatível, dependências de requirements.txt e ferramentas verificadas por scripts/preflight.sh --offline. Os testes offline não exigem login ou acesso a cluster.

## Testes locais

Execute tests/run.sh. A suíte cobre validação de comandos, sanitização, contexto, relatórios e ferramentas MCP com dados sintéticos. Cenários negativos devem negar comandos não permitidos, contexto inconsistente e entradas inválidas sem coletar credenciais.

## Integração consultiva

Em ambiente autorizado, confirme contexto, servidor, usuário e identidade do cluster. Consulte capacidades antes dos recursos. Verifique separadamente sucesso de leitura, RBAC insuficiente, recurso ausente e falha da ferramenta. Nenhum desses resultados, isoladamente, prova causa raiz.

## Must-gather

A coleta não é consulta passiva: pode criar recursos temporários e reunir informações sensíveis. Defina aprovação, escopo, destino privado e sanitização antes de executar. Confira identidade do cluster, artefatos, integridade e remoção dos recursos temporários. Não publique coletas ou credenciais no código.

## Registro e aceite

Para cada cenário, registre SHA, entrada sintética, resultado esperado, observado e evidência em local privado. Use PASS, FAIL, BLOCKED e NOT RUN conforme execução real. Um teste offline não substitui integração; um YAML aceito não comprova diagnóstico correto. Guias operacionais descrevem o procedimento, sem guardar fotografias do ambiente.
