from pydantic import BaseModel

class PokemonCardSchema(BaseModel):
    id: str
    name: str
    number: str
    set: str 
    artist: str | None
    rarity: str | None
    flavor_text: str | None

    def get_view(self):
        from card_display.pokemon_tcg_card_display import PokemonTCGCardDisplay
        return PokemonTCGCardDisplay(self)

