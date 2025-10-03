# AGENTS.md — Regras e Fluxo para Agentes (Codex) no Repositório Django — v2
> **Objetivo:** remover o bloqueio rígido de migrations que estava travando o agente, **liberando a criação/edição de migrations com guarda‑corpos de segurança**, revisão humana e checks automatizados.

---

## 0) O que mudou nesta versão
- ✅ **Migrations estão liberadas para o agente (Codex)**, com regras e checklist de segurança.
- ✅ Mantemos **proibição de segredos/credenciais**, comandos destrutivos e mudanças de infra sem task explícita.
- ✅ Incluímos **fluxo de PR com plano de migração/rollback**, **pré‑commit** e **CI** com verificações simples.
- ✅ Criamos um **“kill switch”** opcional para reativar o bloqueio de migrations quando necessário: o arquivo `.codex-no-migrations` na raiz do repo.

---

## 1) Escopo e Princípios
- Este repo é um **projeto Django** com banco versionado via **migrations** (Django ORM).
- O agente **pode** criar/editar arquivos em `*/migrations/*.py` e alterar modelos, admin, serializers, views, urls e docs.
- O agente **não executa comandos** (ex.: `makemigrations`, `migrate`, `collectstatic`, `pip install`, etc.). Esses comandos são responsabilidade humana/local/CI.
- Evitar downtime: seguir **padrão em duas fases** e **migrações reversíveis**.
- Toda mudança com impacto em dados/esquema precisa de **descrição clara de riscos** e **plano de rollback**.

---

## 2) O que o agente **PODE** fazer
- Alterar **modelos** em `models.py` e gerar as **migrations correspondentes** (schema e, quando necessário, data migrations com `RunPython`).
- Escrever **testes** (unit/integration) e documentação (`README`, `docs/`), além de **scripts** em `management/commands` (sem executá‑los).
- Refatorar código, adicionar tipagem, docstrings, i18n, validações, otimizações com `select_related/prefetch_related`.
- Sugerir pipelines de CI/hooks, anotando que a habilitação é feita por humano.

## 3) O que o agente **NÃO PODE** fazer
- **Segurança/Segredos:** jamais commitar chaves, tokens, `.env`, dumps de banco ou dados pessoais sensíveis.
- **Infra/Ambiente:** não criar/alterar `.venv/`, Docker, Nginx, Gunicorn, `requirements*.txt`/`poetry.lock` sem task explícita.
- **Dados de produção:** não propor comandos que apaguem dados ou SQL destrutivo. Operações destrutivas devem seguir o padrão em duas fases e passar por revisão explícita.
- **Execução de comandos:** o agente gera arquivos; a execução (`makemigrations`, `migrate`, etc.) cabe ao humano/CI.

---

## 4) Convenções para Migrations (guarda‑corpos)
1. **Reversibilidade**: toda `RunPython` deve ter `reverse_code` (evitar `noop` salvo justificativa). Prefira ORM ao invés de `RunSQL`. Se usar `RunSQL`, inclua `reverse_sql`.
2. **Padrão em duas fases** (evitar downtime/locks prolongados):
   - **Fase A (compat)**: adicionar campos com `null=True`/`default` seguro; criar tabelas/índices; duplicar/renomear via add+copy (sem remover ainda).
   - **Backfill**: `RunPython` para preencher valores; criar comandos de manutenção se necessário.
   - **Fase B (restritiva)**: tornar `null=False`/constraints depois do backfill; remover campo antigo **apenas** quando não mais lido. Em PR separado, se possível.
3. **Destrutivo** (`RemoveField`, `DeleteModel`, `AlterField` para mais restrito) só quando:
   - Houver **plano de rollback** claro e **janela** definida; preferir **PR separado**.
   - Houver **confirmação** no PR (label `destructive-ok` ou aprovação humana).
4. **Ordem e dependências**: migrations devem depender da **última** migration do app; evite reordenar históricos.
5. **Dados volumosos**: para tabelas grandes, considerar batch (paginação) e evitar longos locks; documentar estratégia.
6. **Índices**: criar índices em migrations de schema; **não** deixar para “fazer manualmente” sem rationale.
7. **Naming**: use nome/descrição de operações nos commits e PRs (ex.: `migrations(app): add field is_active to Client`).

---

## 5) Fluxo de PR com Migrations (recomendado)
**Pelo agente:**
1. Implementar mudança em `models.py` e gerar as **migrations** necessárias (schema/data).  
2. Abrir PR contendo:
   - **Resumo da mudança** (tabelas/campos afetados, leituras/escritas, performance esperada).
   - **Plano de migração** (Fase A/B se aplicável, passos de backfill, feature flags se houver).
   - **Plano de rollback** (como desfazer; `reverse_code`; impacto).
   - **Checklist de Migrations** (abaixo).

**Checklist de Migrations (copie no PR):**
- [ ] Todas as `RunPython` possuem `reverse_code` significativo.
- [ ] Operações potencialmente destrutivas foram isoladas (fase B) ou possuem label `destructive-ok`.
- [ ] Mudanças restritivas (ex.: `null=False`) ocorrem **após** backfill/comprovação de dados.
- [ ] Índices/constraints foram avaliados e criados quando necessário.
- [ ] Para tabelas grandes, o backfill está em batch (ou documentado por quê não).
- [ ] Testes e admin ajustados (se UI/validações dependem do novo campo).
- [ ] Plano de rollback descrito.

**Pelo humano/CI (exemplo de sequência local):**
```bash
source .venv/bin/activate
python manage.py makemigrations --check --dry-run   # sanity check
python manage.py migrate --plan                    # visualizar plano
pytest -q                                          # se aplicável
# Em staging: python manage.py migrate
```

---

## 6) Pré‑commit (guarda‑corpo leve + “kill switch”)
Crie `.git/hooks/pre-commit` e torne executável (`chmod +x .git/hooks/pre-commit`):
```bash
#!/usr/bin/env bash
set -euo pipefail

# Kill switch global para bloquear migrations (reativa o comportamento antigo se necessário)
if [ -f ".codex-no-migrations" ]; then
  if git diff --cached --name-only | grep -E "^.+/migrations/.+\.py$" >/dev/null; then
    echo "❌ Migrations bloqueadas por '.codex-no-migrations'. Remova o arquivo para liberar."
    exit 1
  fi
fi

# Alerta de operações destrutivas (soft‑block; CI reforça)
if git diff --cached --name-only | grep -E "^.+/migrations/.+\.py$" >/dev/null; then
  if git diff --cached | grep -E "migrations\.(RemoveField|DeleteModel)"; then
    echo "⚠️  Detectado RemoveField/DeleteModel. Garanta fase B, label 'destructive-ok' e plano de rollback."
  fi
  if git diff --cached | grep -E "RunSQL\("; then
    if ! git diff --cached | grep -E "reverse_sql\s*=" >/dev/null; then
      echo "⚠️  RunSQL sem reverse_sql detectado. Adicione reverse_sql ou justifique no PR."
    fi
  fi
fi
```

---

## 7) GitHub Actions (checks sugeridos)
Adicione um job simples de verificação (ajuste conforme seu pipeline):
```yaml
name: migrations-checks
on:
  pull_request:
    types: [opened, synchronize, reopened]
jobs:
  safe-migrations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Detect migrations in PR
        id: mig
        run: |
          set -e
          FILES="$(git diff --name-only origin/${{ github.base_ref }}... | grep -E '^.+/migrations/.+\.py$' || true)"
          echo "files<<EOF" >> $GITHUB_OUTPUT
          echo "${FILES}" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      - name: Block destructive ops unless labeled
        if: steps.mig.outputs.files != ''
        run: |
          set -e
          # bloqueia operações destrutivas se não houver label 'destructive-ok'
          HAS_LABEL=$(echo '${{ toJson(github.event.pull_request.labels) }}' | grep -ci 'destructive-ok' || true)
          if git diff origin/${{ github.base_ref }}... | grep -E 'migrations\.(RemoveField|DeleteModel)'; then
            if [ "$HAS_LABEL" -eq 0 ]; then
              echo "❌ RemoveField/DeleteModel sem label 'destructive-ok'."; exit 1;
            fi
          fi
          # alerta para RunSQL sem reverse_sql
          if git diff origin/${{ github.base_ref }}... | grep -E 'RunSQL\('; then
            if ! git diff origin/${{ github.base_ref }}... | grep -E 'reverse_sql\s*='; then
              echo '⚠️ RunSQL sem reverse_sql detectado. Considere adicionar ou justificar no PR.'
            fi
          fi
```

---

## 8) Padrões de Código/Qualidade (resumo)
- **Tipagem** (quando aplicável) e docstrings claras.
- **i18n**: UI com `gettext_lazy`.
- **Admin**: `list_display`, `search_fields`, `list_filter`, `ordering` e booleans/ícones padronizados.
- **Validações**: `clean()`/validators; `help_text` e `verbose_name` amigáveis.
- **Performance**: atenção a N+1; crie índices quando necessário (em migrations).

---

## 9) Conflitos de migrations (branchs concorrentes)
- Após merges/rebases, o agente **pode** criar uma *merge migration* (ou o humano executa `makemigrations --merge`).  
- Descrever no PR o motivo da *merge migration* e validar importabilidade (CI/local).

---

## 10) FAQ Rápido
**Posso apagar campo direto?** Prefira **duas fases**: parar de ler o campo → backfill/cópia → remover em PR/migração separada com label `destructive-ok` e rollback claro.  
**Posso usar `RunSQL`?** Sim, **desde que** traga `reverse_sql` e justificativa. Prefira ORM.  
**E se der conflito de numeração?** Regerar localmente ou criar *merge migration*. Documente no PR.  
**Quem roda `migrate`?** Humano/CI, não o agente.

---

## 11) TL;DR
- Codex **pode** criar/editar migrations, **desde que** siga: **reversível**, **duas fases**, **destrutivo isolado**, **PR com plano/rollback**.  
- Pré‑commit dá avisos e `.codex-no-migrations` desliga tudo se precisar.  
- CI reforça regras mínimas e exige label para destrutivo.

