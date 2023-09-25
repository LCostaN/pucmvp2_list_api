from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from model import Base
from model.game_game_list import GameGameList
from model.game import Game


class GameList(Base):
    __tablename__ = 'game_list'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    user = Column(String(100), nullable=False)
    games = relationship("Game", secondary=GameGameList.__tablename__, order_by=Game.id)
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

    def __str__(self):
        return "{"+ f"name: {self.name}, description: {self.description}, user: {self.user}, is_private: {self.is_private}" +"}"