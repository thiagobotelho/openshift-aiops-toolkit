# Requisitos e verificação de compatibilidade

| Componente | Requisito / verificação |
|---|---|
| Bash | Confira a versão e execute os testes dos scripts no sistema de destino. |
| Python | 3.10+; confira requirements.txt e pyproject.toml antes de instalar. |
| SDK MCP | Use a versão fixada em requirements.txt; valide handshake e catálogo na mesma venv. |
| oc | Autenticado, no PATH ou configurado por OPENSHIFT_AIOPS_OC_BIN. |
| CRC | Opcional; confira crc status e a identidade da API quando utilizado. |
| jq, tar, gzip, sha256sum | Confira disponibilidade com o preflight offline. |
| Codex CLI / yq / Podman | Opcionais conforme a integração escolhida. |
| OpenShift | Consulte capacidades e RBAC; APIs opcionais podem estar ausentes. |

Execute o [plano de validação](VALIDACAO.md) no destino. A presença de um binário não comprova compatibilidade do produto nem acesso a todos os recursos. Resultados por versão e evidências pertencem ao registro privado da execução.
