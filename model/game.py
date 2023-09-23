from sqlalchemy import Column, Text, String, Integer, DateTime
from datetime import datetime

from model import Base

class Game(Base):
    __tablename__ = 'game'

    id: Column(Integer, primary_key=True)
    title: Column(String(255), nullable=False)
    thumbnail: Column(Text)
    short_description: Column(Text)
    game_url: Column(Text)
    genre: Column(String(255))
    platform: Column(String(255))
    publisher: Column(String(255))
    developer: Column(String(255))
    release_date: Column(DateTime)

    def __init__(self,
                 id: int,
                 title: str,
                 thumbnail: str,
                 short_description: str,
                 game_url: str,
                 genre: str,
                 platform: str,
                 publisher: str,
                 developer: str,
                 release_date: str,
                 ):
        """
        Cria um jogo

        Arguments:
            id: Id
            title: Nome
            thumbnail: Imagem de apresentação
            short_description: Descrição curta
            game_url: URL oficial
            genre: Categoria
            platform: Plataforma (Windows, Linux, Android, etc.)
            publisher: Empresa proprietária responsável pela distribuição do jogo
            developer: Empresa que desenvolveu o jogo
            release_date: Data de lançamento
        """
        self.id = id
        self.title = title
        self.thumbnail = thumbnail
        self.short_description = short_description
        self.game_url = game_url
        self.genre = genre
        self.platform = platform
        self.publisher = publisher
        self.developer = developer
        self.release_date = release_date
