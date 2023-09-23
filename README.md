# MVP 2 - Lista de Jogos API

API de dados para Lista de Jogos

## Descrição

Esta API cuida do armazenamento das Listas de Jogos criadas pelos usuários do projeto FrontEnd do MVP2 - Lucas Nantes.
Esta API não autentica usuários.

## Executando o projeto

Para executar o projeto, é necessário usar a ferramenta docker e criar o container. O Dockerfile já está configurado e só é necessário rodar os comandos:

`docker build -t mvp2_list_api .`
`docker run -d --name mvp2_list_api -p 5000:5000 mvp2_list_api`

## Rotas

### /

* GET - Lista todos as listas públicas
* POST - Cria uma nova Lista de Jogos

### /:id

* GET - Retorna dados de uma lista específica
* PUT - Atualiza a lista específica
* DELETE - Apaga a lista específica

### /me

* GET - Retorna listas do usuário
