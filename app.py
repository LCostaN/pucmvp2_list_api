from flask_openapi3 import OpenAPI, Info, Tag
from sqlalchemy.exc import IntegrityError

from model import Session, GameList
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Game List API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
list_tag = Tag(name="Lista de Jogo",
               description="Adição, visualização e remoção de Lista de Jogos à base")

@app.post('/', tags=[list_tag], responses={"200": GameListViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_list(body: GameListSchema):
    """Adiciona uma nova Lista de Jogos à base de dados
    """
    gamelist = GameList(
        name=body.name,
        description=body.description,
        user=body.user,
        is_private=body.is_private,
    )
    logger.debug(f"Adicionando lista de nome: '{gamelist.name}'")
    try:
        session = Session()
        session.add(gamelist)
        session.commit()
        logger.debug(f"Adicionado lista de nome: '{gamelist.name}'")
        return show_list(gamelist), 200

    except IntegrityError as e:
        error_msg = "Lista de mesmo nome já salvo na base"
        logger.warning(
            f"Erro ao adicionar lista '{gamelist.name}', {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        error_msg = "Não foi possível salvar novo item"
        logger.warning(
            f"Erro ao adicionar lista '{gamelist.name}', {error_msg}")
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
        print(gamelists)
        return show_lists(gamelists), 200


@app.get('/me', tags=[list_tag], responses={"200": GameListSchema, "404": ErrorSchema})
def get_my_lists(query: MyGameListSearchSchema):
    """Busca as listas criadas pelo usuário

    Retorna uma representação dos produtos.
    """
    user = ''
    logger.debug(f"Coletando as listas de #{user}")
    session = Session()
    lists = session.query(GameList).filter(GameList.user == user).all()

    if not lists:
        return {"data": []}, 200
    else:
        logger.debug(f"%d listas encontradas" % len(lists))
        print(lists)
        return show_lists(lists), 200


@app.get('/:id', tags=[list_tag], responses={"200": GameListSchema, "404": ErrorSchema})
def get_list(query: GameListSearchSchema):
    """Faz a busca por uma Lista a partir do id.

    Retorna uma representação da lista se ela for pública ou se o usuário for o dono.
    """
    id = query.id
    logger.debug(f"Coletando dados sobre lista #{id}")
    session = Session()
    list = session.query(GameList).filter(GameList.id == id).first()

    if not list:
        error_msg = "Lista não encontrado na base :/"
        logger.warning(f"Erro ao buscar lista #'{id}', {error_msg}")
        return {"message": error_msg}, 404
    else:
        logger.debug(f"Lista encontrada: '{list.name}'")
        return show_list(list), 200


@app.delete('/:id', tags=[list_tag], responses={"200": {}, "404": ErrorSchema})
def del_list(query: GameListDeleteSchema):
    """Deleta uma Lista a partir do id informado

    Retorna vazio com status de sucesso.
    """
    id = query.id
    logger.debug(f"Deletando lista #{id}")
    session = Session()
    count = session.query(GameList).filter(GameList.id == id).delete()
    session.commit()

    if count:
        logger.debug(f"Lista deletada #{id}")
        return {}
    else:
        error_msg = "Lista não encontrado na base"
        logger.warning(f"Erro ao deletar produto #'{id}', {error_msg}")
        return {"message": error_msg}, 404


@app.put('/:id', tags=[list_tag], responses={"200": GameListSchema, "404": ErrorSchema})
def update_list(query: GameListUpdateQuerySchema, body: GameListUpdateBodySchema):
    """Atualiza a Lista de Jogos identificada pelo id informado, se o usuário for o dono.

    Retorna uma representação da Lista.
    """
    id = query.id
    logger.debug(f"Atualizando lista #{id}")
    try:
        session = Session()
        list: GameList = session.query(
            GameList).filter(GameList.id == id).first()

        if not list:
            error_msg = "Lista não encontrado na base :/"
            logger.warning(f"Lista não encontrada: #{id}, {error_msg}")
            return {"message": error_msg}, 404
        else:
            logger.debug(f"Atualizando lista #{id}")
            list.name = body.name or list.name
            list.description = body.description or list.description
            list.is_private = body.is_private or list.is_private

            if body.games:
                list.games = body.games

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
