# Colmeia Online

Sistema web para controle de colmeias de abelhas, com suporte a múltiplos usuários. Cada pessoa cadastrada pode registrar seus próprios meliponários/apiários, colmeias, espécies manejadas e revisões periódicas. Superusuários têm acesso a todos os dados do sistema.

## Funcionalidades

- Cadastro de espécies com características, comportamento padrão e UFs de ocorrência.
- Registro de meliponários/apiários vinculados ao usuário, com contagem automática de colmeias associadas.
- Gerenciamento completo das colmeias, incluindo histórico de aquisição, situação atual e observações.
- Registro de revisões com notas sobre rainha, cria, alimento, força da colônia, temperamento, peso e manejos executados.
- Upload de anexos (fotos/documentos) relacionados às revisões.
- Separação de dados por usuário (multi-tenant). Usuários comuns visualizam apenas seus próprios cadastros; superusuários têm visão global.

## Modelos principais

### Espécies
- Grupo (Apis mellifera ou Sem ferrão)
- Nome científico e nome popular
- Características gerais
- UFs onde ocorre (seleção múltipla)
- Temperamento padrão (opcional)

### Meliponários/Apiários
- Nome e localização
- Proprietário (usuário que cadastrou)
- Contador automático de colmeias associadas
- Observações

### Colmeias
- Número de identificação automático e único
- Método de aquisição (Compra, Troca, Divisão, Captura ou Doação)
- Origem (opcional) e data de aquisição
- Espécie e nome popular
- Situação da colmeia (produção, observação, órfã, morta, doada/vendida ou perdida)
- Relacionamento opcional com meliponário/apiário do mesmo usuário
- Data da última revisão (atualizada automaticamente)
- Observações

### Revisões
- Colmeia, data/hora da revisão e indicador se a rainha foi vista
- Escalas de 0 a 5 para cria, alimento e força
- Temperamento (Muito mansa, Mansa, Média, Arisca ou Agressiva)
- Peso da colmeia (opcional)
- Observações e registro de manejo (condicional)
- Anexos de arquivos/fotos

## Configuração do projeto

```bash
# Criar a env
python -m venv venv

# Gerar nova secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Colar no arquivo .env

# Ativar a env
source {nome da env}/bin/activate

# Desativar a env
deactivate

# Instalar as dependências
pip install -r requirements.txt

# Criar o banco de dados
python manage.py migrate

# Criar um superusuário
python manage.py createsuperuser

# Iniciar o projeto
python manage.py runserver

# Compilar mensagens de tradução
python manage.py compilemessages

# Atualizar o requirements.txt
pip freeze > requirements.txt

# Coletar arquivos estáticos (produção)
python manage.py collectstatic --noinput
```

### Referências
- [Documentação do django-unfold](https://github.com/unfoldadmin/django-unfold)

Clique [aqui](docs/padroes.md) para ver os padrões de desenvolvimento adotados no projeto.
