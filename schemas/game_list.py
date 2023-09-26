from pydantic import BaseModel, Field
from model import GameList, Game
from typing import Optional, List


class GameListByIdSchema(BaseModel):
    """Define parâmetro de busca por id
    """
    id: int = Field(description="ID da Lista")

class GameListSchema(BaseModel):
    """ Define como uma nova lista de jogos deve ser representada
    """
    name: str = Field(title="Nome", description="Nome da Lista")
    description: Optional[str] = Field(
        title="Descrição", description="Descrição da Lista")
    is_private: bool = Field(
        title="Privacidade", description="Define se a lista pode ser visualizada por outros usuário ou somente o criador")


class GameListViewSchema(BaseModel):
    """ Define como uma lista de jogos será retornada
    """
    id: int = Field(title="ID", description="ID da lista")
    name: str = Field(title="Nome", description="Nome da Lista")
    user: str = Field(title="Usuário", description="Nome do Usuário criador")
    is_private: bool = Field(
        title="Privacidade", description="Define se a lista pode ser visualizada por outros usuário ou somente o criador")
    description: Optional[str] = Field(
        title="Descrição", description="Descrição da Lista")
    games: List = Field(
        title='Jogos', description="Jogos incluídos na lista", default=[])
    
class GameListDeleteViewSchema(BaseModel):
    """ Define como a resposta de uma remoção de lista será representada
    """
    data: bool = Field(title="Sucesso")


class GameListUpdateBodySchema(BaseModel):
    """ Define os parâmetros de atualização de uma lista de jogos.
    """
    name: Optional[str] = Field(title="Nome", description="Nome da Lista")
    description: Optional[str] = Field(title="Descrição", description="Descrição da Lista")
    is_private: Optional[bool] = Field(title="Privacidade", description="Define se a lista pode ser visualizada por outros usuário ou somente o criador")
    games: Optional[List] = Field(title='Jogos', description="Jogos incluídos na lista")


class MyGameListSearchSchema(BaseModel):
    """ Define os parâmetros de busca para as listas de jogos do usuário
    """
    user: str = Field(title="Usuário", description="Nome do Usuário criador")


class GameListListSchema(BaseModel):
    """ Define como uma listagem de lista de jogos será retornada.
    """
    data: List[GameListViewSchema]


def show_lists(lists: List[GameList]):
    """ Retorna uma representação das listas de jogos seguindo o schema definido em
        GameListViewSchema.
    """
    result = []
    for item in lists:
        result.append(show_list(item))

    return {"data": result}


def show_game(game: Game):
    """ Retorna uma representação do jogo que é incluído nas listas
    """
    return {
        "id": game.id,
        "title": game.title,
        "thumbnail": game.thumbnail,
        "short_description": game.short_description,
        "game_url": game.game_url,
        "genre": game.genre,
        "platform": game.platform,
        "publisher": game.publisher,
        "developer": game.developer,
        "release_date": game.release_date,
    }


def show_list(gamelist: GameList):
    """ Retorna uma representação da Lista de Jogos seguindo o schema definido em
        GameListViewSchema.
    """
    games = []
    for item in gamelist.games:
        games.append(show_game(item))

    return {
        "id": gamelist.id,
        "name": gamelist.name,
        "description": gamelist.description,
        "user": gamelist.user,
        "is_private": gamelist.is_private,
        "games": games,
    }
