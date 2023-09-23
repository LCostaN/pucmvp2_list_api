from model import Base
from sqlalchemy import Column, Table, ForeignKey

# association table
game_game_list = Table(
    "game_game_list",
    Base.metadata,
    Column("game_id", ForeignKey("game.id"), primary_key=True),
    Column("game_list_id", ForeignKey("game_list.id"), primary_key=True),
)