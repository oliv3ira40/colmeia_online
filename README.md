### Esboço do projeto:

### Comandos úteis

```bash

# Criar a env
$ python -m venv venv

# Gerar nova secret key
$ python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Colar no arquivo .env

# Ativar a env
$ source {nome da env}/bin/activate

# Desativar a env
$ deactivate

# Iniciar o projeto
$ python manage.py runserver

# Criar o banco de dados
$ python manage.py migrate

# Criar um super usuário
$ python manage.py createsuperuser

# Compilar as mensagens
$ python manage.py compilemessages

# Criar arquivo requirements.txt
$ pip freeze > requirements.txt

# Mandar dependências para o arquivo requirements.txt
$ pip freeze > requirements.txt

# Instalar as dependências
$ pip install -r requirements.txt

# Link para a documentação do unfold:
[Git Django Unfold](https://github.com/unfoldadmin/django-unfold)

# Reiniciar o gunicorn e o nginx
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

```

<!-- django-admin makemessages -l pt_BR -d django -->

### Padrões de desenvolvimento
Clique [aqui](docs/padroes.md) para ver os padrões de desenvolvimento utilizados neste projeto.



<!--
    Trata-se de um sistema para gerenciar colmeias de abelhas, 
    com funcionalidades para cadastrar, editar e visualizar informações sobre as colmeias, 
    bem como registrar inspeções/revisões e tratamentos realizados.

    ### Modelos

    Colmeias
        N. de identificação -> somente leitura, gera o número automaticamente, precisa ser único
        Método de aquisição -> escolha entre: Compra, Troca, Divisão e Captura, Doação
        Data de aquisição -> data
        Espécie -> escolha entre: Apis mellifera, Lista de espécies sem ferrão
        Nome Popular -> texto
        Situação -> escolha entre:
            - Em produção (colônia saudável/ativa)
            - Em observação (fraca, recém-capturada, em adaptação)
            - Órfã (sem rainha)
            - Morta
            - Doada/Vendida
            - Perdida (desaparecida, roubada)
        Meliponário / Apiário -> referência (opcional) a um meliponário ou apiário cadastrado
        Observações -> texto livre
        Revisões -> relação com o modelo Revisões

    Revisões
        Colmeia -> referência à colmeia
        Data da revisão -> data/hora
        Rainha vista -> booleano
        Cria -> escala 0 a 5 (nível de criação presente)
        Alimento/Reservas -> escala 0 a 5
        Força da colônia -> escala 0 a 5
        Temperamento -> escolha entre: Muito mansa, Mansa, Média, Arisca, Agressiva
        Observações -> texto livre
        Arquivos/Fotos -> múltiplos anexos relacionados
        Houve manejo? -> booleano
            Se sim exibir campo: Descrever manejo(s) realizado(s)

    Espécies
        Grupo -> Apis mellifera ou Sem ferrão
        Nome científico -> texto
        Nome popular -> texto
        Características -> texto livre
        UF -> escolha múltipla entre as unidades federativas do Brasil

    Meliponários/Apiários
        Nome -> texto
        QTD de colmeias vinculadas -> número, preenchido automaticamente com a contagem de colmeias associadas
-->


<!-- documentação tema django-admin-interface -->
<!-- https://github.com/fabiocaccamo/django-admin-interface?tab=readme-ov-file -->
<!-- python manage.py loaddata admin_interface_theme_bootstrap.json -->
