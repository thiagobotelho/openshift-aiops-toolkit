# Validação must-gather CRC — 2026-07-12

Esta validação confirma o fluxo completo de must-gather controlado no CRC/OpenShift Local usando o contexto atual do `oc`.

## Identidade validada

- Contexto: `crc-admin`
- API: `https://api.crc.testing:6443`
- Usuário: `kubeadmin`
- OpenShift: `4.22.1`
- Cluster detectado: `crc-tg922`

## Escopo

Executado com confirmação explícita:

```bash
export OPENSHIFT_AIOPS_OC_BIN="$HOME/.crc/cache/crc_libvirt_4.22.1_amd64/oc"
export OPENSHIFT_AIOPS_MUST_GATHER_CONFIRM="crc-tg922"
python3 -m mcp_server.commands must-gather --timeout 900
```

Não foram executados:

- commit/push de dados brutos;
- alteração manual de recursos;
- leitura de conteúdo de Secrets pelo toolkit;
- publicação automática do pacote;
- remoção automática de artefatos brutos.

## Resultado da coleta

- Diretório local: `evidencias/crc-tg922/20260712-204403-788319/must-gather`
- Classificação: `CONFIDENCIAL — NÃO PUBLICAR`
- Exit code do must-gather: `0`
- Duração: `37.907s`
- Arquivos brutos: `4331`
- Tamanho bruto aproximado: `199441515 bytes`
- Checksums: PASSOU
- Análise offline: PASSOU
- Pods/namespaces residuais `must-gather`: não encontrados na validação pós-coleta

## Análise offline

Resumo gerado pelo toolkit:

- arquivos brutos indexados: `4331`;
- achados potenciais de sensibilidade: `1294`;
- domínios com evidências: ClusterVersion, ClusterOperators, nodes, events, pods, storage, network, monitoring, OLM e certificates.

Os achados de sensibilidade são esperados para must-gather e reforçam que `raw/` não deve ser publicado sem revisão.

## Ressalvas

1. O diretório `evidencias/**` é ignorado pelo Git e deve permanecer local.
2. A análise offline é conservadora e não substitui revisão humana antes de compartilhamento.
3. A validação usa `kubeadmin`; RBAC limitado não é exercitado nesse cenário.
4. Quando `crc` não está no `PATH` da sessão, o `oc` pode ser apontado explicitamente via `OPENSHIFT_AIOPS_OC_BIN`.

## Conclusão

Fluxo de must-gather aprovado para laboratório CRC/OpenShift Local, desde que os dados brutos permaneçam locais e confidenciais.
