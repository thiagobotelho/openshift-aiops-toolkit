from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from .sanitizers import sanitize_text

def generate_base_report(evidence_dir: Path | None = None, title: str = 'Relatório de Diagnóstico OpenShift') -> str:
    now = datetime.now().isoformat(timespec='seconds')
    manifest_text = 'Manifesto não informado.'
    if evidence_dir and (evidence_dir / 'manifest.json').exists():
        manifest_text = (evidence_dir / 'manifest.json').read_text(encoding='utf-8')
    manifest_text = sanitize_text(manifest_text)
    return f"""# {title}

## Identificação

- Data: {now}
- Escopo: diagnóstico assistivo somente leitura
- Evidências: {str(evidence_dir) if evidence_dir else 'não informado'}

## Resumo executivo

Nenhuma causa raiz definitiva deve ser afirmada sem evidência suficiente.

## Saúde geral

Consulte ClusterVersion, ClusterOperators, nodes, workloads, storage, network, eventos e monitoring nos artefatos.

## Achados

Use `templates/achado.md` para registrar ACH-001, ACH-002 e demais achados.

## Manifesto sanitizado

```json
{manifest_text[:6000]}
```

## Recomendações

- Validar hipóteses com comandos somente leitura.
- Aprovar remediações fora do toolkit.
- Executar validação pós-mudança e comparar coletas.
"""

def _load_manifest(path: Path) -> dict:
    p = path / 'manifest.json'
    if not p.exists():
        return {}
    return json.loads(sanitize_text(p.read_text(encoding='utf-8')))

def compare_evidence_dirs(old: Path, new: Path) -> str:
    a, b = _load_manifest(old), _load_manifest(new)
    return f"""# Comparação de Coletas

## Coleta antiga

- Caminho: `{old}`
- Cluster: {a.get('cluster', 'desconhecido')}
- Horário: {a.get('started_at', 'desconhecido')}

## Coleta nova

- Caminho: `{new}`
- Cluster: {b.get('cluster', 'desconhecido')}
- Horário: {b.get('started_at', 'desconhecido')}

## Diferenças iniciais

- Comandos antigos: {len(a.get('commands', []))}
- Comandos novos: {len(b.get('commands', []))}
- Arquivos antigos: {len(a.get('files', []))}
- Arquivos novos: {len(b.get('files', []))}

Revise novos sintomas, itens resolvidos, regressões e diferenças de versão/capacidade.
"""
