from sqlalchemy import func, select
from database.managers.user_manager import UserNotExistError
from database.models.user_card_model import UserCardModel
from database.models.user_model import UserModel
from database.session import get_session
from drops.card_drop_event import CardDropEvent
from schemas.pokemon_card_schema import PokemonCardSchema
from utils.card_utils import CardUtil

class UserCardManager:
    
    async def create_cards_for_drop(tcg_cards, drop_event_id):
        cards = []
        async with get_session() as session:
            for card in tcg_cards:
                user_card = UserCardModel()
                user_card.pokemon_tcg_card_id = card.id
                user_card.drop_event_id = drop_event_id

                user_card.pattern_number = CardUtil.get_random_pattern_number()
                user_card.float_value = CardUtil.get_random_float_value()

                result = await session.execute(
                    select(func.max(UserCardModel.print_number)).filter_by(
                        pokemon_tcg_card_id=card.id
                    )
                )

                max_print_number: int = result.scalar() or 0
                new_print_number = max_print_number + 1

                user_card.print_number = new_print_number

                session.add(user_card)
                cards.append(user_card)
            await session.commit()
            return cards
    
    @staticmethod
    async def claim_card_id(discord_user_id: int, user_card_id: int) -> UserCardModel:
        async with get_session() as session:
            db_user = await session.get(UserModel, discord_user_id)
            if db_user is None:
                raise UserNotExistError(f"User with id:{discord_user_id} does not exist.")

            user_card = await session.get(UserCardModel, user_card_id) 
            if user_card is None:
                raise CardNotExistError(f"Card with id:{user_card_id} does not exist.")
            
            if user_card.owner_id is not None:
                raise CardAlreadyClaimedError(f"Card with id: {user_card_id} is already claimed.")
            
            user_card.owner_id = discord_user_id
            await session.commit()
            return user_card


class CardNotExistError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        # You can customize the string representation of the error
        return f"Card Not Exist: {self.message}"

class CardAlreadyClaimedError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        # You can customize the string representation of the error
        return f"Card Already Claimed: {self.message}"



            

