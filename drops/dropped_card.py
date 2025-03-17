from database.models.user_card_model import UserCardModel
from schemas.pokemon_card_schema import PokemonCardSchema


class DroppedCard:
    def __init__(self, tcg_card, user_card):
        self.tcg_card: PokemonCardSchema = tcg_card
        self.user_card: UserCardModel = user_card