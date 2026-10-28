# Evidência e limites do diagnóstico


Consulte primeiro contexto, identidade e capacidades. Ferramentas somente leitura podem falhar por RBAC sem que o cluster esteja degradado. Os exemplos de RBAC estão em docs/examples; não conceda Secrets, exec ou mutação por conveniência. Guarde evidências sanitizadas fora do código e diferencie hipótese de causa comprovada.


## Compatibilidade do SDK MCP

O servidor usa a API de ferramentas do SDK MCP 1.x. requirements.txt fixa a versão validada e pyproject.toml impede resolver a versão 2 sem migração explícita. Execute o teste de inicialização/catálogo com o SDK instalado; o modo alternativo sem dependência não comprova compatibilidade do SDK.

## Diagnóstico de políticas

Use as consultas somente leitura para identificar namespaces, labels e políticas. A coleta do toolkit não substitui evidência de um fluxo ou uma decisão do proxy. Correlacione hora e IP nos sistemas de observabilidade autorizados; não amplie a allowlist para exec, patch ou leitura de Secrets por conveniência.
