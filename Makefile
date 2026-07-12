SHELL := /usr/bin/env bash
CLUSTER ?=
CONTEXT ?=
ENVIRONMENT ?=
KUBECONFIG ?=
NS ?=
POD ?=
KIND ?= deployment
NAME ?=
OP ?=
NODE ?=
RESOURCE ?=
OLD ?=
NEW ?=
OUTPUT ?= human
TIMEOUT ?= 60
VERBOSE ?=
COMMON_ARGS =
ifneq ($(ENVIRONMENT),)
COMMON_ARGS += --environment $(ENVIRONMENT)
endif
ifneq ($(CLUSTER),)
COMMON_ARGS += --cluster $(CLUSTER)
endif
ifneq ($(CONTEXT),)
COMMON_ARGS += --context $(CONTEXT)
endif
ifneq ($(KUBECONFIG),)
COMMON_ARGS += --kubeconfig $(KUBECONFIG)
endif
CLI_ARGS = --output $(OUTPUT) --timeout $(TIMEOUT)
ifneq ($(CONTEXT),)
CLI_ARGS += --context $(CONTEXT)
endif
ifneq ($(KUBECONFIG),)
CLI_ARGS += --kubeconfig $(KUBECONFIG)
endif
ifneq ($(VERBOSE),)
CLI_ARGS += --verbose
endif
.PHONY: help install uninstall check check-cluster list-clusters context health collect cluster operators nodes pods pod workload namespace operator node storage network ingress dns api etcd auth monitoring certificates capacity events olm upgrade must-gather-preflight must-gather analyze-must-gather inspect report sanitize bundle compare mcp test lint clean
help: ## Mostra ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "%-22s %s\n", $$1, $$2}'
install: ## Instala ambiente local
	@scripts/install.sh
uninstall: ## Remove ambiente virtual local
	@scripts/uninstall.sh
check: ## Executa preflight local/offline sem acessar cluster
	@scripts/preflight.sh --offline $(COMMON_ARGS)
check-cluster: ## Executa preflight consultivo contra o cluster atual
	@scripts/preflight.sh $(COMMON_ARGS)
list-clusters: ## Lista clusters do inventário
	@scripts/listar-clusters.sh
context: ## Mostra contexto atual
	@scripts/validar-contexto.sh $(COMMON_ARGS)
health: ## Coleta diagnóstico resumido
	@./openshift-aiops health $(CLI_ARGS)
collect: ## Coleta evidências gerais do cluster
	@scripts/coletar-cluster.sh $(COMMON_ARGS)
cluster: ## Mostra identidade do cluster atual
	@./openshift-aiops cluster $(CLI_ARGS)
operators: ## Lista/resume ClusterOperators
	@./openshift-aiops operators $(CLI_ARGS)
nodes: ## Lista/resume nodes
	@./openshift-aiops nodes $(CLI_ARGS)
pods: ## Lista/resume pods problemáticos
	@./openshift-aiops pods $(CLI_ARGS)
pod: ## Diagnostica Pod: make pod NS=ns POD=pod
	@test -n "$(NS)" && test -n "$(POD)"
	@scripts/diagnosticar-pod.sh $(NS) $(POD) $(COMMON_ARGS)
workload: ## Diagnostica workload
	@test -n "$(NS)" && test -n "$(NAME)"
	@scripts/diagnosticar-workload.sh $(NS) $(NAME) --kind $(KIND) $(COMMON_ARGS)
namespace: ## Diagnostica namespace
	@test -n "$(NS)"
	@scripts/diagnosticar-namespace.sh $(NS) $(COMMON_ARGS)
operator: ## Diagnostica operador
	@test -n "$(OP)"
	@scripts/diagnosticar-operator.sh $(OP) $(COMMON_ARGS)
node: ## Diagnostica node
	@test -n "$(NODE)"
	@scripts/diagnosticar-node.sh $(NODE) $(COMMON_ARGS)
storage: ## Diagnóstico de storage
	@./openshift-aiops storage $(CLI_ARGS)
network: ## Diagnóstico de rede
	@./openshift-aiops network $(CLI_ARGS)
ingress: ## Diagnóstico de ingress
	@./openshift-aiops ingress $(CLI_ARGS)
dns: ## Diagnóstico de DNS
	@./openshift-aiops dns $(CLI_ARGS)
api: ## Diagnóstico de API
	@scripts/diagnosticar-api.sh $(COMMON_ARGS)
etcd: ## Diagnóstico de etcd
	@scripts/diagnosticar-etcd.sh $(COMMON_ARGS)
auth: ## Diagnóstico de authentication
	@scripts/diagnosticar-authentication.sh $(COMMON_ARGS)
monitoring: ## Diagnóstico de monitoring
	@./openshift-aiops monitoring $(CLI_ARGS)
certificates: ## Diagnóstico de certificados e CSRs
	@./openshift-aiops certificates $(CLI_ARGS)
capacity: ## Capacidade dos nodes
	@./openshift-aiops capacity $(CLI_ARGS)
events: ## Eventos Warning recentes
	@./openshift-aiops events $(CLI_ARGS)
olm: ## Diagnóstico de OLM
	@./openshift-aiops olm $(CLI_ARGS)
upgrade: ## Verifica status de upgrade
	@scripts/verificar-upgrade.sh $(COMMON_ARGS)
must-gather-preflight: ## Preflight consultivo de must-gather
	@scripts/preflight.sh $(COMMON_ARGS) >/dev/null
	@python3 -m mcp_server.commands must-gather-preflight $(COMMON_ARGS)
must-gather: ## Coleta must-gather com confirmação humana
	@scripts/coletar-must-gather.sh $(COMMON_ARGS)
analyze-must-gather: ## Analisa must-gather offline: make analyze-must-gather RESOURCE=evidencias/.../must-gather
	@test -n "$(RESOURCE)"
	@python3 -m mcp_server.commands analyze-must-gather --path $(RESOURCE)
inspect: ## Coleta inspect seletivo
	@test -n "$(RESOURCE)"
	@scripts/coletar-inspect.sh $(RESOURCE) $(COMMON_ARGS)
report: ## Gera relatório Markdown
	@scripts/gerar-relatorio.sh $(COMMON_ARGS)
sanitize: ## Sanitiza evidências
	@test -n "$(RESOURCE)"
	@scripts/sanitizar-evidencias.sh --path $(RESOURCE)
bundle: ## Empacota evidências
	@test -n "$(RESOURCE)"
	@scripts/empacotar-evidencias.sh --path $(RESOURCE)
compare: ## Compara coletas
	@test -n "$(OLD)" && test -n "$(NEW)"
	@scripts/comparar-coletas.sh --old $(OLD) --new $(NEW)
mcp: ## Inicia servidor MCP stdio
	@python3 -m mcp_server.server
test lint: ## Executa testes e validações estáticas
	@tests/run.sh
clean: ## Remove caches locais do projeto
	@python3 -c "from pathlib import Path; import shutil; [shutil.rmtree(p) for p in [Path('.pytest_cache'), Path('.mypy_cache'), Path('.ruff_cache')] if p.exists()]; [shutil.rmtree(p) for p in Path('.').rglob('__pycache__')]"
