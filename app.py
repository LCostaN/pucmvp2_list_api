from flask import request
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
list_tag = Tag(name="Lista de Jogo",
               description="Adição, visualização e remoção de Lista de Jogos à base")

@app.post('/', tags=[list_tag], security=security, responses={
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


@app.get('/', tags=[list_tag], responses={"200": GameListListSchema, "404": ErrorSchema})
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


@app.get('/me', tags=[list_tag], security=security, responses={"200": GameListSchema, "404": ErrorSchema})
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

@app.get('/:id', tags=[list_tag], security=security, responses={"200": GameListSchema, "404": ErrorSchema})
def get_list(query: GameListSearchSchema):
    """Faz a busca por uma Lista a partir do id.

    Retorna uma representação da lista se ela for pública ou se o usuário for o dono.
    """
    id = query.id
    logger.debug(f"Coletando dados sobre lista #{id}")
    
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


@app.delete('/:id', tags=[list_tag], security=security, responses={"200": GameListDeleteViewSchema, "404": ErrorSchema})
def del_list(query: GameListDeleteSchema):
    """Deleta uma Lista a partir do id informado

    Retorna vazio com status de sucesso.
    """
    id = query.id

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


@app.put('/:id', tags=[list_tag], security=security, responses={"200": GameListSchema, "404": ErrorSchema})
def update_list(query: GameListUpdateQuerySchema, body: GameListUpdateBodySchema):
    """Atualiza a Lista de Jogos identificada pelo id informado, se o usuário for o dono.

    Retorna uma representação da Lista.
    """
    id = query.id
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
            list.games = body.games
        
        session.add(list)
        session.commit()

        return show_list(list), 200

    except IntegrityError as e:
        logger.warning(
            f"Erro ao atualizar lista #{id}, {e}")
        return {"message": error_msg}, 409

    except Exception as e:
        error_msg = "Não foi possível atualizar a lista"
        logger.error(f"Erro ao atualizar lista #{id}', {e}")
        return {"message": error_msg}, 400
