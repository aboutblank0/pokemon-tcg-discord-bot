from pathlib import Path
from pydantic import BaseModel

class PokemonCardSetSchema(BaseModel):
    id: str
    name: str
    series: str
    printed_total: int
    total: int
    release_date: str