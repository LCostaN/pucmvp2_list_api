from flask import request, redirect
from flask_openapi3 import OpenAPI, Info, Tag
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from model import Session, GameList
from logger import logger
from schemas import *
from flask_cors import CORS

from utils import readToken

jwt = {
  "type": "http",
  "scheme": "bearer",
  "bearerFormat": "JWT"
}

security_schemes = {"jwt": jwt}
security = [{"jwt": []}]

info = Info(title="Game List API", version="1.0.0")
app = OpenAPI(__name__, info=info, security_schemes=security_schemes)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
list_tag = Tag(name="Lista de Jogo",
               description="Adição, visualização e remoção de Lista de Jogos à base")

@app.get('/', tags=[home_tag])
def redirect_to_docs():
    """Redireciona para a tela de documentação do Swagger
    """
    return redirect('/openapi/swagger')

@app.post('/list/', tags=[list_tag], security=security, responses={
    "200": GameListViewSchema, 
    "401": ErrorSchema, 
    "409": ErrorSchema, 
    "400": ErrorSchema,
    })
def add_list(body: GameListSchema):
    """Adiciona uma nova Lista de Jogos à base de dados
    """
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return {"message": "Nenhum usuário autenticado"}, 401
        
        token = bearer.split()[1]
        user = readToken(token).get('username')

        if not user:
            return {"message": "Nenhum usuário autenticado"}, 401
        
        gamelist = GameList(
            name=body.name,
            description=body.description,
            user=user,
            is_private=body.is_private,
        )
        
        logger.debug(f"Adicionando lista de nome: '{gamelist.name}'")
        session = Session()
        session.add(gamelist)
        session.commit()

        return show_list(gamelist), 200

    except IntegrityError as e:
        error_msg = "Lista de mesmo nome já salvo na base"
        logger.warning(f"Erro ao criar lista, {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        error_msg = "Não foi possível salvar novo item"
        logger.error(f"ERRO AO CRIAR LISTA, {e}")
        return {"message": error_msg}, 400


@app.get('/list/', tags=[list_tag], responses={"200": GameListListSchema, "404": ErrorSchema})
def get_lists():
    """Busca todas as listas públicas. Uma lista é pública quando o valor de is_private é falso.

    Retorna uma listagem com o resultado encontrado.
    """
    logger.debug(f"Coletando listas ")
    session = Session()
    gamelists = session.query(GameList).filter(
        GameList.is_private == False).all()

    if not gamelists:
        return {"data": []}, 200
    else:
        logger.debug(f"%d listas encontradas" % len(gamelists))
        return show_lists(gamelists), 200


@app.get('/list/me', tags=[list_tag], security=security, responses={"200": GameListSchema, "404": ErrorSchema})
def get_my_lists():
    """Busca as listas criadas pelo usuário

    Retorna uma representação dos produtos.
    """
    bearer = request.headers.get('Authorization')
    if not bearer:
        return {"message": "Nenhum usuário autenticado"}, 401
    
    try:
        token = bearer.split()[1]
        user = readToken(token).get('username')

        if not user:
            return {"message": "Nenhum usuário autenticado"}, 401
        
        logger.debug(f"Coletando as listas de #{user}")
        session = Session()
        lists = session.query(GameList).filter(GameList.user == user).all()

        if not lists:
            return {"data": []}, 200
        else:
            logger.debug(f"%d listas encontradas" % len(lists))
            return show_lists(lists), 200
    except Exception as e:
        logger.warning(f"Erro buscando listas por usuário, {e}")
        return {"data": []}, 400

@app.get('/list/<int:id>', tags=[list_tag], security=security,responses={"200": GameListSchema, "404": ErrorSchema})
def get_list(path: GameListByIdSchema):
    """Faz a busca por uma Lista a partir do id.

    Retorna uma representação da lista se ela for pública ou se o usuário for o dono.
    """
    id = path.id
    user = None
    bearer = request.headers.get('Authorization')

    if bearer and len(bearer.split()) > 1:
        token = bearer.split()[1]
        user = readToken(token).get('username')

    session = Session()
    list = session.query(GameList).filter(GameList.id == id).filter(or_(GameList.is_private == False, GameList.user == user)).first()

    if not list:
        error_msg = "Lista não encontrada"
        logger.warning(f"Erro ao buscar lista #'{id}', {error_msg}")
        return {"message": error_msg}, 404
    else:
        logger.debug(f"Lista encontrada: '{list.name}'")
        return show_list(list), 200


@app.delete('/list/<int:id>', tags=[list_tag], security=security, responses={"200": GameListDeleteViewSchema, "404": ErrorSchema})
def del_list(path: GameListByIdSchema):
    """Deleta uma Lista a partir do id informado

    Retorna vazio com status de sucesso.
    """
    id = path.id
    bearer = request.headers.get('Authorization')
    if not bearer:
        return {"message": "Nenhum usuário autenticado"}, 401
    
    token = bearer.split()[1]
    user = readToken(token).get('username')

    if not user:
        return {"message": "Nenhum usuário autenticado"}, 401

    logger.debug(f"Deletando lista #{id}")
    session = Session()
    count = session.query(GameList).filter(GameList.id == id, GameList.user == user).delete()
    session.commit()

    if count:
        logger.debug(f"Deletada a Lista #{id}")
        return {"data": True}, 200
    else:
        error_msg = "Lista não encontrado na base"
        return {"message": error_msg}, 404


@app.put('/list/<int:id>', tags=[list_tag], security=security, responses={"200": GameListSchema, "404": ErrorSchema})
def update_list(path: GameListByIdSchema, body: GameListUpdateBodySchema):
    """Atualiza a Lista de Jogos identificada pelo id informado, se o usuário for o dono.

    Retorna uma representação da Lista.
    """
    id = path.id
    logger.debug(f"Atualizando lista #{id}")
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return {"message": "Nenhum usuário autenticado"}, 401
        
        token = bearer.split()[1]
        user = readToken(token)['username']
        
        if not user:
            return {"message": "Nenhum usuário autenticado"}, 401
        
        session = Session()
        list: GameList = session.query(GameList).filter(GameList.id == id, GameList.user == user).first()

        if not list:
            error_msg = "Lista não encontrada"
            logger.warning(f"Lista não encontrada: #{id}")
            return {"message": error_msg}, 404
        
        logger.debug(f"Atualizando lista #{id}")
        if body.name is not None:
            list.name = body.name
        if body.description is not None:
            list.description = body.description
        if body.is_private is not None:
            list.is_private = body.is_private
        if body.games is not None:
            list.games = []
            for item in body.games:
                game:Game = session.query(Game).filter(Game.id == item['id']).first()
                
                if not game:
                    game = Game(
                        item['id'],
                        item['title'],
                        item['thumbnail'],
                        item['short_description'],
                        item['game_url'],
                        item['genre'],
                        item['platform'],
                        item['publisher'],
                        item['developer'],
                        item['release_date']
                    )
                    session.add(game)

                list.games.append(game)
        
        session.add(list)
        session.commit()

        return show_list(list), 200

    except IntegrityError as e:
        error_msg = "Não foi possível atualizar a lista"
        logger.warning(f"INTEGRITY ERROR #{id}, {e}")
        return {"message": error_msg}, 409

    except Exception as e:
        error_msg = "Não foi possível atualizar a lista"
        logger.error(f"ERRO DESCONHECIDO', {e}")
        return {"message": error_msg}, 400
