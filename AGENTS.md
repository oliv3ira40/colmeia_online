# AGENTS.md — Regras e Fluxo para Agentes (IA) neste Repositório Django

> **Objetivo:** evitar problemas de **venv errado**, **migrations divergentes**, código inseguro e PRs difíceis de revisar quando um agente (IA) gera trechos de código para este projeto.

---

## 1) Escopo e Princípios

- Este repositório é um **projeto Django** com banco de dados versionado por **migrations**.
- **As migrations são versionadas no Git**. Elas **não** devem ser criadas/alteradas por agentes.
- O agente **não executa comandos**: nada de `pip install`, `makemigrations`, `migrate`, `collectstatic`, etc.
- O agente gera **apenas código-fonte** (Python/JS/CSS/HTML/Docs) sob as regras deste arquivo.

---

## 2) Convenções do Repositório

- Um **venv por projeto**, chamado `.venv` na raiz. O agente **não** cria/edita venv.
- Python suportado: definido no `pyproject.toml`/`runtime.txt`/`Dockerfile` (quando existirem).
- **Migrations SEMPRE versionadas.** Não usar `.gitignore` para ignorá-las.
- Secretos/variáveis de ambiente nunca em repositório: **não** tocar `.env`, `settings_secrets.py`, etc.

---

## 3) O que o AGENTE **NÃO PODE** fazer

1. **Migrations**
   - Criar, editar, apagar qualquer arquivo em `*/migrations/*.py`.
   - Sugerir rodar `makemigrations`, `migrate`, `--fake`, `sqlmigrate`.
   - Alterar `MIGRATION_MODULES` em `settings.py`.

2. **Ambiente/Infra**
   - Criar/alterar `.venv/`, `requirements*.txt`, `poetry.lock`, `Pipfile.lock` sem pedido explícito humano.
   - Rodar comandos de sistema, gerenciar pacotes ou tocar em Docker/Nginx/Gunicorn sem task clara.

3. **Segurança/Config**
   - Comitar chaves, tokens, credenciais, `.env`.
   - Modificar autenticação/autorização sensível sem análise de impacto.

4. **Banco/Prod Data**
   - Fornecer comandos que **apaguem dados** ou executem SQL destrutivo sem *feature flag* e plano de rollback.

---

## 4) O que o AGENTE **PODE** fazer

- Alterar **modelos** em `models.py` e camadas relacionadas (`admin.py`, `forms.py`, `serializers.py`, `views.py`, `urls.py`), **sem** tocar nas migrations.
- Escrever/adaptar **tests** (unitários/integrados) e documentações (`README.md`, `docs/`).
- Refatorar código, adicionar **tipagem**, docstrings, `help_text`, `verbose_name`, mensagens de validação.
- Propor **scripts de manutenção** (ex.: `management/commands`) – sem rodá-los.
- Sugerir **snippets de CI/hooks** (pre-commit/Actions), marcando claramente que precisam de habilitação humana.

---

## 5) Fluxo quando houver alterações de MODELOS (schema)

**Pelo agente:**
1. Ajustar apenas os **arquivos de código** (ex.: `app/models.py`, `admin.py`), mantendo **compatibilidade reversa** quando possível:
   - Campos novos com `null=True` e/ou `default=` quando necessário.
   - Migrações de dados sensíveis **apenas como TODO** em comentários.

2. Abrir PR com **descrição clara**:
   - “Este PR altera modelos. **Não** inclui migrations por política do repositório.”
   - Lista de arquivos alterados e impacto esperado (leitura/escrita/performance).

**Pelo humano (pós-merge/rebase do PR do agente):**
```bash
source .venv/bin/activate
python manage.py makemigrations
python manage.py migrate
pytest -q      # se aplicável
git add */migrations/*.py
git commit -m "chore(migrations): gera migrations após alterações do agente"
```

**Se houver conflitos entre branches:**
```bash
python manage.py makemigrations --merge
python manage.py migrate
git add */migrations/*.py
git commit -m "chore(migrations): merge migration"
```

> **Nota:** `--fake` só em DEV e com plena certeza de que o estado do banco reflete aquela migração. Evitar em produção.

---

## 6) Mensagem padrão para o agente anexar quando mexer em modelos

> **Nota de migrações:** Conforme política do repositório, **não** gere/edite arquivos em `migrations/`. As alterações de modelo serão migradas manualmente por um desenvolvedor humano com `python manage.py makemigrations && python manage.py migrate` (e *merge migrations* após merges/rebases).

---

## 7) Padrões de Código e Qualidade

- **Tipagem**: use `from __future__ import annotations` quando aplicável; adicione tipos em funções/métodos.
- **Docstrings**: breve descrição, parâmetros, retorno e exceções relevantes.
- **i18n**: strings para UI com `gettext_lazy` (`from django.utils.translation import gettext_lazy as _`).
- **Django Admin**: inclua `list_display`, `search_fields`, `list_filter`, `ordering`, ícones/booleans padronizados.
- **Validações**: use `clean()`/validators; mensagens amigáveis; `help_text`/`verbose_name` adequados.
- **Testes**: se criar lógica não-trivial, inclua testes. Use `pytest`/`unittest` conforme padrão do repo.
- **Performance**: prefira `select_related/prefetch_related` quando necessário; evite N+1; índices em migrations **devem ser sinalizados como TODO** na descrição para o humano gerar.

---

## 8) Branch/Commit/PR — Convenções

- **Branch name** (pelo agente): `codex/<breve-descricao-kebab>`
- **Commits** (pelo agente): `feat(app): <mensagem>` / `fix(app):` / `refactor(app):` / `docs:` / `test:` / `chore:`
- **PR template** deve incluir (o agente preenche):
  - Escopo e impacto.
  - “Sem migrations” (se houver mudança em modelos).
  - Checklist (abaixo).

**Checklist do PR do agente:**
- [ ] Nenhum arquivo em `*/migrations/` foi criado/modificado/removido.
- [ ] Alterações limitadas a código-fonte e/ou docs/tests.
- [ ] Compatibilidade reversa razoável (quando envolve modelos/DB).
- [ ] Docstrings, `help_text`, `verbose_name` e mensagens de erro revisadas.
- [ ] TODOs claros onde o humano deverá gerar migrations de dados/índices.

---

## 9) Snippets úteis (uso a critério do humano)

### 9.1 Hook de pre-commit (bloqueia migrations por agente; alerta sobre migrações faltantes)
Crie `.git/hooks/pre-commit` e dê permissão `chmod +x .git/hooks/pre-commit`:
```bash
#!/usr/bin/env bash
# Bloqueia commits do agente que mexam em migrations (ajuste a detecção do ator se necessário)
if git config user.name | grep -qi "agent\|bot\|codex"; then
  if git diff --cached --name-only | grep -E "^.+/migrations/.+\.py$" >/dev/null; then
    echo "❌ Política: o agente não pode commitar migrations."
    exit 1
  fi
fi

# (Opcional) Garanta venv ativo
which python | grep -q "/.venv/" || { echo "❌ Ative o venv (.venv)."; exit 1; }

# (Opcional) Alerta se mudanças de modelos exigem migrations
python manage.py makemigrations --check --dry-run >/dev/null 2>&1 ||   echo "⚠️ Há alterações de modelo que exigem migrations (gerar manualmente)."
```

### 9.2 CODEOWNERS (revisão humana obrigatória em migrations)
Crie `CODEOWNERS` na raiz:
```
**/migrations/*.py  @seu-usuario-ou-time
```

### 9.3 GitHub Actions (bloquear migrations do agente)
Job de verificação simples (ajuste `seu-bot`):
```yaml
- name: Block agent migrations
  run: |
    if [ "${{ github.actor }}" = "seu-bot" ]; then
      if git diff --name-only origin/${{ github.base_ref }}... | grep -E '^.+/migrations/.+\.py$'; then
        echo "❌ O agente não pode alterar migrations."; exit 1;
      fi
    fi
```

### 9.4 Verificações de consistência (opcional no CI)
```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q  # se aplicável
```

---

## 10) Como o revisor humano valida um PR do agente

1. Conferir **se não há migrations no diff**.
2. Rodar localmente:
   ```bash
   source .venv/bin/activate
   python manage.py makemigrations --check --dry-run
   pytest -q  # se aplicável
   ```
3. Se houver modelos alterados: **gerar migrations localmente**, aplicar e commitar em PR separado ou após merge.
4. Confirmar padrões (docstrings/i18n/ajustes no admin/validadores).
5. Aprovar o PR.

---

## 11) FAQ Rápido

**1. Devemos ignorar migrations no Git?**  
Não. Migrations são versionadas para garantir reprodutibilidade e deploy confiável.

**2. O agente pode propor migrations?**  
Pode sugerir *em texto* o que a migration faria (ex.: “índice em campo X”), mas **não** criar o arquivo.

**3. E *--fake*?**  
Apenas em **desenvolvimento** e com total certeza do estado real do banco. Evitar em produção.

**4. E se outro branch também alterou modelos?**  
Após merge/rebase, o **humano** roda `makemigrations --merge` e commita a *merge migration*.

---

> **Resumo:** O agente **não cria migrations**, não executa comandos, e mantém alterações restritas ao código-fonte com boa documentação. O humano gera/aplica/commita migrations no momento certo. Assim evitamos divergências e histórico inconsistente.
