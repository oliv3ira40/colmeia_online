# Colmeia Online

Sistema web para controle de colmeias de abelhas, com suporte a múltiplos usuários. Cada pessoa cadastrada pode registrar seus próprios meliponários/apiários, colmeias, espécies manejadas e revisões periódicas. Superusuários têm acesso a todos os dados do sistema.

## Funcionalidades

- Cadastro de espécies com características, comportamento padrão e UFs de ocorrência.
- Registro de meliponários/apiários vinculados ao usuário, com contagem automática de colmeias associadas.
- Gerenciamento completo das colmeias, incluindo histórico de aquisição, situação atual e observações.
- Registro de revisões com notas sobre rainha, cria, alimento, pólen, força da colônia, temperamento, peso e manejos executados.
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
- Cria (Nenhuma, Pouca, Moderada ou Abundante)
- Alimento/Reservas (Nenhum, Pouco, Moderado ou Abundante)
- Pólen (Nenhum, Pouco, Moderado ou Abundante)
- Força da colônia (Fraca, Média ou Forte)
- Temperamento (Muito mansa, Mansa, Média, Arisca ou Agressiva)
- Peso da colmeia (opcional)
- Observações e descrição livre de manejos realizados
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

# Reiniciar o serviço (produção)
sudo systemctl restart colmeia_online
```

### Seeds de dados

Os arquivos de seed ficam em `apiary/management/commands/` e podem ser executados via `python manage.py <comando>`. Todos os comandos são idempotentes: rodá-los novamente atualiza os registros existentes sem gerar duplicações.

#### Espécies

Para importar ou atualizar as espécies padrão de abelhas sem ferrão use o comando `seed_species`.

```bash
# Carrega espécies a partir de docs/especies.json
python manage.py seed_species
```

O comando lê o arquivo JSON indicado (`docs/especies.json`), cria novas espécies e atualiza registros existentes com o mesmo `nome_cientifico`. Cada item da lista deve informar o campo `grupo`; quando o valor estiver ausente ou inválido, o grupo padrão `sem_ferrao` é utilizado automaticamente.

#### Modelos de caixas

Use o comando `seed_box_models` para carregar a lista de modelos de caixas de criação.

```bash
python manage.py seed_box_models
```

O seed cria/atualiza os modelos com os respectivos nomes e descrições padronizadas (INPA, PNN, SH, Moreira (USP), JCW, AF, Novy, Didática, Cacuí, Kerr, Capel, Baiano, Isis, Maria e Juliane).

#### Cidades do Brasil

Para popular o cadastro de cidades utilize o comando `seed_cities`, que consome o arquivo `docs/estados-cidades.json`.

```bash
python manage.py seed_cities
```

Cada registro do JSON contém uma sigla de estado e a lista de cidades correspondentes. O comando gera entradas no formato `Cidade - UF`, mantendo o cadastro atualizado sem criar duplicatas.

### Tema utilizado no admin
As páginas criadas devem seguir o tema bootstrap do django-admin-interface, que oferece uma interface mais amigável e moderna para o administrador do Django.
- [Documentação do django-admin-interface](https://github.com/fabiocaccamo/django-admin-interface?tab=readme-ov-file)
- Intalação do tema bootstrap do django-admin-interface: python manage.py loaddata admin_interface_theme_bootstrap.json
- Para customizar templates do admin, é necessário consultar a documentação/arquivos do template, por exemplo: https://github.com/fabiocaccamo/django-admin-interface/blob/main/admin_interface/templates/admin/base_site.html

Clique [aqui](docs/padroes.md) para ver os padrões de desenvolvimento adotados no projeto.

- **Boas práticas de migrations (Django)**: consulte o guia em [`docs/boas-praticas-migrations.md`](docs/boas-praticas-migrations.md).

### Modelos

    **Colmeias**
    - N. de identificação → somente leitura, gerado automaticamente, único
    - Método de aquisição → escolha entre: Compra, Troca, Divisão, Captura, Doação
    - Origem da colmeia → texto (opcional)
    - No caso de compra, qual a data de aquisição → data
    - Data de transferência para a caixa → data (obrigatória somente para capturas)
    - Colmeia de origem → referência a outra colmeia (obrigatória somente para divisões)
    - Modelo de caixa → referência opcional à lista de Modelos de caixas
    - Espécie → referência ao modelo Espécies
    - Nome Popular → texto
    - Situação → escolha entre:
        - Em produção (colônia saudável/ativa)
        - Em observação (fraca, recém-capturada, em adaptação)
        - Órfã (sem rainha)
        - Morta
        - Doada/Vendida
        - Perdida (desaparecida, roubada)
    - Meliponário / Apiário → referência (opcional) a um meliponário ou apiário cadastrado
    - Data da última revisão → preenchido automaticamente
    - Observações → texto livre
    - Revisões → relação com o modelo Revisões

    **Revisões**
    - Colmeia → referência à colmeia
    - Data da revisão → data/hora
    - Tipo de revisão → Revisão de rotina, Divisão, Tratamento, Alimentação ou Colheita
    - Rainha vista → booleano
    - Cria → escolher entre: Nenhuma, Pouca, Moderada, Abundante
    - Alimento/Reservas → escolher entre: Nenhum, Pouco, Moderado, Abundante
    - Pólen → escolher entre: Nenhum, Pouco, Moderado, Abundante
    - Força da colônia → escolher entre: Fraca, Média, Forte
    - Temperamento → escolha entre: Muito mansa, Mansa, Média, Arisca, Agressiva
    - Peso da colmeia (opcional) → número
    - Observações → texto livre
    - Descreva manejo(s) realizado(s) -> texto livre
    - Informações de colheita (opcionais, exibidas quando o tipo é Colheita): quantidades de mel, própolis, cera e pólen colhidos + observações específicas
    - Informações de alimentação (opcionais, exibidas quando o tipo é Alimentação): tipos e quantidades de alimentos energéticos/proteicos fornecidos + observações
    - Arquivos/Fotos → múltiplos anexos relacionados

    **Espécies**
    - Grupo → Apis mellifera ou Sem ferrão
    - Nome científico → texto
    - Nome popular → texto
    - Características → texto livre
    - UF → escolha múltipla entre as unidades federativas do Brasil
    - Temperamento padrão (opcional) → texto

    **Meliponários/Apiários**
    - Nome → texto
    - Localização (cidade/estado) → texto
    - Responsável/Proprietário -> usuário que cadastrou o meliponário/apiário
    - QTD de colmeias vinculadas → número, preenchido automaticamente com a contagem de colmeias associadas
    - Observações → texto livre
