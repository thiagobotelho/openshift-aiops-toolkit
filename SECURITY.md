# Segurança

Este projeto foi desenhado para operação assistiva e somente leitura em OpenShift.

## Modelo de ameaça

Riscos considerados: prompt injection, parâmetro malicioso, contexto incorreto, execução acidental em produção, vazamento de token/senha/kubeconfig, coleta excessiva, manipulação de caminhos locais, symlink, path traversal e logs com credenciais.

## Controles implementados

- allowlist de comandos de leitura;
- catálogo de bloqueio para verbos de escrita;
- validação estrita de parâmetros Kubernetes;
- timeout e truncamento de saída;
- sanitização antes de logar, salvar evidências, gerar relatórios ou responder via MCP;
- `umask 077` nos scripts;
- confirmação adicional para produção;
- nenhum acesso ao conteúdo de Secrets;
- nenhuma ferramenta MCP genérica de terminal.
