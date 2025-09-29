### Padrões de desenvolvimento

- Git Flow
    - [Indicadores](docs/flow-indicators.png)

    - [Flow](docs/flow.png)

    - Padrão de versionamento: [Semantic Versioning 2.0.0](https://semver.org/lang/pt-BR/)


- Padrões de branchs, escritas em inglês
    ```bash
    # Exemplos de branchs:
    $ git checkout -b feature/branch-test
    $ git checkout -b refactor/branch-test
    $ git checkout -b chore/branch-test
    $ git checkout -b bugfix/branch-test
    $ git checkout -b fix/branch-test
    ```

- Padrões de commits, escritos em inglês e seguindo a doc: [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/)
    ```bash
    # Exemplos de commits:
    $ git commit -q -m "feat: commit description"
    $ git commit -q -m "refactor: commit description"
    $ git commit -q -m "chore: commit description"
    $ git commit -q -m "bugfix: commit description"
    $ git commit -q -m "fix: commit description"
    ```

- Padrões de Merge requests, escritos em português (prefixo + breve descrição do mr)
    ```bash
    # Exemplos de merge requests:
    Adicionada a função "custom_get_posts"
    Refatorada a função "custom_get_posts"
    Alterada a função "custom_get_posts"
    Removida a função "custom_get_posts"
    Corrigida a função "custom_get_posts"
    ```
