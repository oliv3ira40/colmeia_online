# AGENTS.md — Colmeia Online

Guia para **agentes/contêineres** (ex.: Codex) prepararem, validarem e executarem o projeto **Colmeia Online** automaticamente.

> **Resumo:** criar venv, instalar dependências, aplicar migrações, coletar estáticos, expor `/static/` e `/media/`, rodar checks e comandos utilitários (ex.: `seed_species`).

---

## ✅ Objetivo
Padronizar o _setup_ do ambiente de execução (com internet habilitada) e os comandos de verificação para que `python manage.py check` e o servidor funcionem sem erros.

---

## 🔧 Pré‑requisitos do Agente
- **Acesso à internet do agente: habilitado** (para instalar `pip` packages).  
- **Shell Bash** disponível.
- Python 3.10+ (recomendado 3.12).

> Se o agente não tiver internet, use _wheels offline_ e ajuste o script para `pip install --no-index --find-links=./wheels -r requirements.txt`.

---

## 🔑 Variáveis de Ambiente
Configure no painel do agente (ou `.env`), conforme o ambiente.

### Obrigatórias (dev)
- `DJANGO_SETTINGS_MODULE=colmeia_online.settings`
- `SECRET_KEY=<gera_com_o_Django>`
- `DEBUG=True`
- `ALLOWED_HOSTS=*`

### Opcionais
- `DATABASE_URL=postgres://...` (se você **não** usar SQLite)
- `LANG=pt_BR.UTF-8`
- `PYTHONDONTWRITEBYTECODE=1`
- `PYTHONUNBUFFERED=1`

> Se usar `.env`, garanta que o projeto lê via `python-dotenv` ou código equivalente.

---

## 📦 Dependências relevantes
- `Django` (4.2.x recomendado)
- `django-admin-interface` (tema do admin)
- `django-colorfield` (dependência do tema)
- `Pillow` (imagens)
- `python-dotenv` (opcional, para `.env`)

> Mantenha o arquivo `requirements.txt` atualizado: `pip freeze > requirements.txt`

---

## 🗂️ Estrutura de arquivos esperada (trecho)
```
colmeia_online/
├─ manage.py
├─ colmeia_online/
│  ├─ settings.py
│  ├─ urls.py
│  └─ ...
├─ apps/...
├─ static/                 # opcional em dev (arquivos do projeto)
├─ staticfiles/            # destino do collectstatic (produção)
├─ media/                  # uploads (logos/anexos)
├─ docs/especies.json      # usado por seed_species
└─ requirements.txt
```

---

## 📜 Script de Configuração (automático)
Use este bloco **como script único** do agente (Codex). Ele configura e valida tudo de ponta a ponta.

```bash
set -euo pipefail

# 1) Virtualenv
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate

# 2) Pip upgrade + dependências
python -m pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
else
  echo "requirements.txt não encontrado!"
  exit 1
fi

# 3) Migrações
python manage.py migrate --noinput

# 4) Coleta de estáticos (não quebra em dev)
python manage.py collectstatic --noinput || true

# 5) Checks
python manage.py check

# 6) Compila mensagens (ignora se não houver locale)
python manage.py compilemessages || true

# 7) Comando utilitário (opcional): popular espécies
if [ -f "docs/especies.json" ]; then
  python manage.py seed_species || true
fi

# 8) Exibe onde o tema foi instalado (debug)
python - <<'PY'
try:
    import admin_interface, pkgutil, sys
    print("admin_interface:", admin_interface.__file__)
except Exception as e:
    print("Aviso: admin_interface não importou ->", e, file=sys.stderr)
PY

echo "Setup finalizado com sucesso."
```

---

## 🔁 Rotina de Validação
1. **Checar apps e config:**  
   ```bash
   python manage.py check
   ```
2. **Rodar servidor dev:**  
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
3. **Criar superusuário (se necessário):**  
   ```bash
   python manage.py createsuperuser
   ```
4. **Popular espécies padrão (opcional):**  
   ```bash
   python manage.py seed_species
   ```

---

## 🌐 Static e Media (importante)
Em **desenvolvimento** (`DEBUG=True`), certifique-se de que `settings.py` tenha:
```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# optional:
# STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

E em `urls.py` (somente com `DEBUG=True`):
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Em **produção**, sirva `/static/` (de `STATIC_ROOT`) e `/media/` (de `MEDIA_ROOT`) via Nginx/Apache.

---

## 🧪 Matriz de Comandos Úteis
```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Banco e estáticos
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Verificações
python manage.py check
python manage.py compilemessages

# Administração
python manage.py createsuperuser

# Dados auxiliares
python manage.py seed_species
```

---

## ❗ Troubleshooting Rápido

### ModuleNotFoundError: No module named 'admin_interface'
- Dependências não instaladas ou agente sem internet.  
- Solução: habilite internet do agente **ou** use wheels offline e rode `pip install -r requirements.txt` antes dos comandos do Django.  
- Confira se `INSTALLED_APPS` está assim (ordem importa):
  ```python
  INSTALLED_APPS = [
      "admin_interface",
      "colorfield",
      "django.contrib.admin",
      "django.contrib.auth",
      "django.contrib.contenttypes",
      "django.contrib.sessions",
      "django.contrib.messages",
      "django.contrib.staticfiles",
      # suas apps...
  ]
  ```

### Logo/anexos não aparecem
- Garanta `MEDIA_ROOT`/`MEDIA_URL` e rotas em `urls.py` no dev.  
- Em prod, sirva `/media/` no Nginx/Apache.  
- Verifique permissões de escrita na pasta `media/`.

### CSS do admin não carrega em produção
- Faltou `collectstatic` ou `/static/` não está servido pelo servidor web.  
- Rode `python manage.py collectstatic --noinput` e ajuste Nginx/Apache para apontar `STATIC_ROOT`.

---

## ✅ Boas práticas
- Mantenha `requirements.txt` atualizado.  
- Não coloque segredos no repositório; use variáveis de ambiente/segredos do agente.  
- Use `ALLOWED_HOSTS` adequado ao host do contêiner.  
- Para Docker/devcontainer, rode o script acima em `postCreateCommand`/`postStartCommand`.
