from model import Base
from sqlalchemy import Column, ForeignKey, Integer

# association table
class GameGameList(Base): 
    __tablename__ = 'game_game_list'

    game_id = Column(Integer, ForeignKey("game.id"), primary_key=True)
    game_list_id = Column(Integer, ForeignKey("game_list.id"), primary_key=True)