from pydantic import BaseModel, Field
from model import GameList
from typing import Optional, List


class GameListSchema(BaseModel):
    """ Define como uma nova lista de jogos deve ser representada
    """
    date: str = Field(title="Vaga", description="Data e Hora do gameList", default="12/07/2023 08:30")
    name: str = Field(title="Nome Pet", description="Nome do Pet", default="Rex")
    src: Optional[str] = Field(title="Foto Pet", description="Imagem do Pet (URL)", default="https://placehold.co/600x400")

class GameListViewSchema(BaseModel):
    """ Define como uma lista de jogos será retornada
    """
    id: int = Field(title="Id", description="Id do gameList", default="1")
    date: str = Field(title="Vaga", description="Data e Hora do gameList", default="12/07/2023 08:30")
    name: str = Field(title="Nome Pet", description="Nome do Pet", default="Rex")
    src: str = Field(title="Foto Pet", description="Imagem do Pet (URL)", default="https://placehold.co/600x400")

    
class ListSearchSchema(BaseModel):
    """ Define os parâmetros de busca da listagem de listas de jogos
    """

class GameListListSchema(BaseModel):
    """ Define como uma listagem de lista de jogos será retornada.
    """
    data: List[GameListViewSchema]

def present_list(lists: List[GameList]):
    """ Retorna uma representação das listas de jogos seguindo o schema definido em
        GameListViewSchema.
    """
    result = []
    for item in lists:
        result.append(apresenta_agendamento(item))

    return {"schedules": result}

def apresenta_agendamento(gameList: GameList):
    """ Retorna uma representação da Lista de Jogos seguindo o schema definido em
        GameListViewSchema.
    """
    date = gameList.date.strftime("%d/%m/%Y %H:%M")
    return {
            "id": gameList.id,
            "name": gameList.name,
            "date": date,
            "src": gameList.src,
        }