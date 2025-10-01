# Boas práticas de migrations (Django)

Este guia resume políticas, checklists e procedimentos para manter o histórico de migrations consistente entre DEV/QA/PROD e evitar erros como `FieldDoesNotExist: <Model> has no field named '<campo>'`.

## Regras principais
1. **Nunca** edite/apague migrations já commitadas/aplicadas.
2. **Sempre** gere **nova migration** para cada mudança em `models.py`.
3. Use a estratégia **Expandir → Deploy → Contrair** para zero/min‑downtime.
4. Antes do deploy: `makemigrations --check` e `migrate --plan`.
5. Em PROD: **backup**, migre e **depois** dê reload no app.
6. Se precisar `--fake`, **documente** o motivo e o ambiente (PR/CHANGELOG).

---

## Política de migrations

- **Proibido reescrever o passado**  
  Não edite, renomeie ou apague migrations já commitadas e aplicadas em qualquer ambiente.  
  Exceção: *squash* formal (veja seção “Regras de squash”) com garantia de que **todos os ambientes** já passaram pela versão substituta.

- **Cada mudança de models → nova migration atômica**  
  Prefira migrations pequenas e focadas (criar campo, alterar tipo, remover índice etc.).  
  Separe **schema** de **migração de dados** pesados.

- **Compatibilidade progressiva (Expand/Contract)**  
  - **Expandir** (compatível com código antigo): adicionar novas colunas/índices/constraints opcionais; popular dados de forma idempotente.  
  - **Deploy do código novo** (usa o novo schema, porém ainda compatível).  
  - **Contrair**: remover colunas/constraints antigas e *feature flags*.

- **Nada de hotfix direto no banco**  
  Alterações manuais no DB só com migration correspondente. Se for emergencial, crie a migration retroativa assim que possível.

- **`--fake` só com justificativa**  
  Use `--fake`/`--fake-initial` apenas para corrigir descompasso de *state*; **registre** em PR/CHANGELOG o comando, motivo e ambiente.

---

## Checklist de CI/CD (antes do deploy)

1. Garantir que não há mudanças sem migration:
   ```bash
   python manage.py makemigrations --check
   ```

2. Inspecionar o plano a ser aplicado:
   ```bash
   python manage.py migrate --plan
   ```

3. Testes e checagens:
   ```bash
   pytest -q            # ou o runner adotado
   python manage.py check
   ```

4. (Recomendado) Ensaiar migrations em **staging** com dump recente de PROD.

5. Revisão no PR:
   - Não houve edição de migrations antigas?
   - Nome e escopo claros?
   - Data migration é idempotente/reentrante?

---

## Playbook de deploy (Django + Gunicorn/Nginx)

> Exemplo com PostgreSQL/Gunicorn; adapte ao seu stack.

**0) Backup do banco (obrigatório):**
```bash
pg_dump -U <user> -h <host> -Fc -d <dbname> > /root/backup_$(date +%F).dump
```

**1) Atualizar código e dependências:**
```bash
git pull
source .venv/bin/activate
pip install -r requirements.txt
```

**2) Aplicar migrations:**
```bash
python manage.py migrate --plan   # revisar plano
python manage.py migrate          # aplicar
```

**3) Coletar estáticos (se aplicável):**
```bash
python manage.py collectstatic --noinput
```

**4) Reload/Restart do app (graceful se possível):**
```bash
sudo systemctl reload gunicorn    # preferível (graceful)
# ou
sudo systemctl restart gunicorn
```

**5) Smoke tests pós-deploy:**
```bash
python manage.py check
# Abrir /admin e rotas críticas no navegador
```

> **Importante:** parar o servidor **não corrige** divergências de migrations; apenas evita erros durante migrações pesadas/destrutivas. O que previne o problema é disciplina com migrations e o checklist pré‑deploy.

---

## Zero/min‑downtime – Padrão Expand/Contract (exemplo)

**Cenário:** renomear campo `A` → `B` em `ModelX`.

1. **Expandir**
   - `AddField B` (nullable/default).
   - Data migration: copiar `A → B` (idempotente).
   - Código: passar a ler/escrever `B`, mantendo compat. com `A` via *feature flag* se necessário.

2. **Deploy do código**

3. **Contrair**
   - Remover usos de `A` no código.
   - `RemoveField A` na migration.

4. **Deploy final** (sem `A`).

**Benefício:** evita que código novo leia coluna que “ainda” não existe ou que código antigo quebre com coluna já removida.

---

## Regras de squash

- Use:
  ```bash
  python manage.py squashmigrations <app> <from_migration> <to_migration>
  ```
- No arquivo squashado, mantenha `replaces = [...]` até **todos os ambientes** passarem a usar o squash.
- Só remova as migrations antigas quando **não houver** mais ambientes executando as intermediárias.

---

## Procedimentos de emergência (divergência DEV × PROD)

**Sintoma clássico:**
```
django.core.exceptions.FieldDoesNotExist: <Model> has no field named "<campo>"
```

**Causa provável:** PROD parou numa migration antiga (ex.: `0001`) e seu histórico atual tem `0002/0003` que assumem a existência passada de um campo que foi removido/squashado do histórico.

**Passos seguros:**

1. **Backup do DB (obrigatório).**

2. **Inspecionar plano:**
   ```bash
   python manage.py migrate <app> --plan
   ```

3. **Se as migrations problemáticas _apenas_ referem o campo inexistente e não criam outras estruturas necessárias:**  
   “Pular” com `--fake` e aplicar o resto:
   ```bash
   python manage.py migrate <app> 0002 --fake
   python manage.py migrate <app> 0003 --fake
   python manage.py migrate
   ```
   > **Sempre documente** no PR/CHANGELOG.

4. **Se há outras operações importantes nessas migrations:**  
   - **Ajustar a migration** (remover operações que referem o campo inexistente) **ou**
   - Criar uma migration de **estado** com `SeparateDatabaseAndState` para alinhar o *state* sem tocar o banco e permitir que as próximas rodem.
   - Depois:
     ```bash
     python manage.py migrate
     ```

5. **Verificações:**
   ```bash
   python manage.py check
   python manage.py makemigrations --check
   ```

---

## DOs & DON'Ts

**✅ DO**
- Gerar migrations pequenas e claras.
- Usar Expand/Contract para mudanças destrutivas.
- Rodar `--plan` e `--check` antes de migrar.
- Documentar qualquer `--fake`.
- Testar migrations em staging com dump de PROD.

**❌ DON'T**
- Editar/apagar migrations já aplicadas.
- Fazer alterações manuais no DB sem migration.
- Misturar schema grande com refactors extensos no mesmo PR.
- Usar `--fake` para “passar por cima” sem entender as consequências.

---

## Template de checks rápidos (para colar no PR)

- [ ] `python manage.py makemigrations --check` passou  
- [ ] `python manage.py migrate --plan` revisado no PR  
- [ ] Migrations seguem Expand/Contract quando aplicável  
- [ ] Não houve edição de migrations antigas  
- [ ] (Opcional) Ensaiado em dump de PROD/staging  
- [ ] Instruções de deploy incluídas (se envolver `--fake`)  

---

## Extras / comandos úteis

**Mostrar histórico por app**
```bash
python manage.py showmigrations <app>
```

**Ver plano até uma migration específica**
```bash
python manage.py migrate <app> 0005 --plan
```

**Criar migration vazia para data‑migration manual**
```bash
python manage.py makemigrations <app> --empty -n data_migrate_something
```

**Exemplo `SeparateDatabaseAndState` (corrige apenas o state, não toca o DB)**
```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('app', '0001_initial')]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='revision',
                    name='management_performed',
                    field=models.BooleanField(default=False),
                ),
            ],
        ),
    ]
```

---

## Notas finais

- Parar o servidor **não** previne problemas de histórico. O que previne é disciplina com migrations e checklist pré‑deploy.
- Para mudanças pesadas ou potencialmente quebradiças, use janela de manutenção curta **ou** a estratégia **Expand/Contract** em duas fases.

> Última atualização: 2025‑09‑30
