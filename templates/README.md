# Templates

Esta pasta contém modelos Markdown para registrar análise, achados, handover e validação.

Templates não são preenchidos automaticamente em todos os campos. Eles são modelos para documentação operacional baseada nas evidências coletadas.

## Estado atual

Os templates estão prontos para uso manual.

Use em conjunto com:

- `evidencias/<cluster>/<timestamp>/`;
- `relatorios/relatorio-diagnostico.md`;
- prompts de análise;
- runbooks do sintoma investigado.

## Quando usar cada template

| Template | Uso |
| --- | --- |
| `achado.md` | Registrar um achado técnico individual. |
| `relatorio-diagnostico.md` | Estruturar diagnóstico técnico completo. |
| `relatorio-executivo.md` | Comunicar impacto e decisão para gestão. |
| `relatorio-incidente.md` | Documentar incidente com timeline e evidências. |
| `relatorio-tecnico.md` | Detalhar causa provável, hipóteses e validações. |
| `plano-remediacao.md` | Propor ações, risco, rollback e critério de sucesso. |
| `validacao-pos-mudanca.md` | Registrar evidência depois da correção. |
| `timeline-incidente.md` | Organizar sequência temporal do incidente. |
| `handover.md` | Transferir contexto entre turnos/equipes. |

## Exemplo

```bash
cp templates/achado.md relatorios/achado-001-pod-crashloop.md
```

Depois preencha usando evidências reais. Não registre tokens, senhas ou conteúdo bruto de Secrets.
