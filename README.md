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
  - No caso de compra, qual a data de aquisição
  - No caso de divisão, de qual colmeia foi originada
  - No caso de captura, em qual data fez a transferência para a caixa
- Origem (opcional)
- Data de aquisição
- Espécie
- Nome popular
- Situação da colmeia (produção, observação, órfã, morta, doada/vendida ou perdida)
- Relacionamento opcional com meliponário/apiário do mesmo usuário
- Data da última revisão (atualizada automaticamente)
- Observações
- Foto da colmeia (opcional)
- Modelo de caixa (opcional), referência a lista (Modelos de caixas abaixo)

### Modelos de caixas (Abaixo temos nome e descrição)
    - INPA: (Fernando Oliveira) – Modular vertical (ninho, sobreninho, melgueiras). É o padrão mais difundido no Brasil pela facilidade de manejo, divisão e coleta de mel. Dimensões variam por espécie (ex.: jataí, mandaçaia, uruçu etc.).
    - PNN: (Paulo Nogueira-Neto) – Horizontal com “gavetas”; muito usado para jataí e mandaçaias. Facilita acessar crias, mas não é o melhor para extrair mel em grande volume.
    - SH: Pensada para espécies que fazem crias em “cachos” (Frieseomelitta, Leurotrigona/“lambe-olhos” etc.) e para facilitar divisões, com compartimentos horizontais e visores.
    - Moreira (USP): Muito usada para Frieseomelitta varia (“marmelada”), focada em eficiência de divisão e manejo dessas espécies de crias em cachos.
    - JCW: Variação modular com melgueiras laterais (existe versão em “T”). Útil em cenários específicos, mas exige mais tampas/isolamentos.
    - AF: (Ailton Fontana) – Módulos “encaixados” num gabinete externo (tipo gaveteiro). Bom isolamento, porém construção/manutenção mais complexas e propolização pode atrapalhar.
    - Novy: (circular, concreto celular/argamassa) – Alta inércia térmica/acústica; pavimentos circulares com alturas adequadas aos potes de alimento. Interessante para controle térmico.
    - Didática (com visores) – Foco educativo/observação; pode servir para manejo leve.
    - Cacuí (família Schwade) – Adaptação vertical inspirada no INPA, criada na Amazônia (reservas Amanã/Mamirauá).
    - Kerr, Capel (horizontal/vertical), Baiano, Isis, Maria, Juliane – Modelos menos comuns ou variações regionais com usos mais nichados.

### Revisões
- Colmeia (referência obrigatória)
- Tipo de revisão (Revisão de rotina, Divisão, Tratamento, Alimentação, Colheita)
  - Em caso de colheita (Todos os campos são opcionais) isso não é um campo e sim uma condição para exibir os campos abaixo
    - Quantidade de mel colhida (em ml)
    - Quantidade de própolis colhida (em gramas)
    - Quantidade de cera colhida (em gramas)
    - Quantidade de pólen colhida (em gramas)
    - Observações específicas sobre a colheita
  - Em caso de alimentação (Todos os campos são opcionais) isso não é um campo e sim uma condição para exibir os campos abaixo
    - Tipo de alimento energético fornecido (Xarope, Mel de Apis, Mel de ASF)
    - Quantidade de alimento energético fornecido (em ml ou gramas)
    - Tipo de alimento proteico fornecido (Bombom de Pólen, Bombom Soja, Pasta de Pólen, Pasta de Soja)
    - Quantidade de suplemento proteico fornecido (em gramas)
    - Observações específicas sobre a alimentação
- Data/hora da revisão
- Indicador se a rainha foi vista
- Cria (Nenhuma, Pouca, Moderada ou Abundante)
- Alimento/Reservas (Nenhum, Pouco, Moderado ou Abundante)
- Pólen (Nenhum, Pouco, Moderado ou Abundante)
- Força da colônia (Fraca, Média ou Forte)
- Temperamento (Muito mansa, Mansa, Média, Arisca ou Agressiva)
- Peso da colmeia (opcional)
- Observações e descrição livre de manejos realizados
- Anexos de arquivos/fotos

### Cidades do Brasil
# Utilizar arquivo estados-cidades.json presente na pasta docs, vou precisar de uma seed para ele tbm
- Nome (deve ser concatenação de cidade - estado, ex.: "Goiânia - GO")

### Lista de criadores por região (opcional)
# A ideia dessa tabela é promover networking entre criadores, facilitando contato e troca de experiências. Cada usuário pode optar por se registrar ou não nessa lista pública, e pode editar ou remover seus dados a qualquer momento. quando ele se inscrever, ele terá acesso aos outros inscritos, mas só pode editar os próprios dados. esses regras precisam estar claras na tabela presente na home do site.
- Nome do criador -> obrigatório
- Localização (cidade/estado) -> escolha entre as cidades cadastradas no sistema -> obrigatório
- Espécies criadas -> escolha múltipla entre espécies cadastradas no sistema -> opcional
- Telefone (WhatsApp) -> obrigatório

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

### Carregar espécies padrão

Para importar ou atualizar as espécies padrão de abelhas sem ferrão use o comando de management `seed_species`.

```bash
# Carrega espécies a partir de docs/especies.json
python manage.py seed_species
```

O comando lê o arquivo JSON indicado, cria novas espécies e atualiza registros existentes com o mesmo `nome_cientifico`. Cada item da lista deve informar o campo `grupo`; quando o valor estiver ausente ou inválido, o grupo padrão `sem_ferrao` é utilizado automaticamente.

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
    - Data de aquisição → data
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
    - Rainha vista → booleano
    - Cria → escolher entre: Nenhuma, Pouca, Moderada, Abundante
    - Alimento/Reservas → escolher entre: Nenhum, Pouco, Moderado, Abundante
    - Pólen → escolher entre: Nenhum, Pouco, Moderado, Abundante
    - Força da colônia → escolher entre: Fraca, Média, Forte
    - Temperamento → escolha entre: Muito mansa, Mansa, Média, Arisca, Agressiva
    - Peso da colmeia (opcional) → número
    - Observações → texto livre
    - Arquivos/Fotos → múltiplos anexos relacionados
    - Houve manejo? → booleano (Excluir campo, não é mais necessário)
    - Descreva manejo(s) realizado(s) -> texto livre

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
