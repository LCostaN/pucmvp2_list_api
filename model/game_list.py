from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from model import Base, Game, game_game_list


class GameList(Base):
    __tablename__ = 'game_list'

    id = Column(Integer, primary_key=True)
    name = Column(DateTime, nullable=False)
    description = Column(Text)
    user = Column(String(100), nullable=False)
    games = relationship("Game", secondary=game_game_list, order_by=Game.id)
    is_private = Column(Boolean, default=True)
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default=datetime.now())

    def __init__(self, name, description, user, is_private=True):
        """
        Cria um Lista de Jogos

        Arguments:
            name: Nome da Lista
            description: Descrição
            user: Nome do usuário criador
            is_private: Pública ou privada
        """
        self.name = name
        self.description = description
        self.user = user
        self.is_private = is_private
