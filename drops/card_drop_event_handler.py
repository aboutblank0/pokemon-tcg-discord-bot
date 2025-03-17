from datetime import datetime
import typing
import uuid
import pytz
from database.managers.user_card_manager import UserCardManager
from database.models.card_drop_event_model import CardDropEventModel
from database.models.user_card_model import UserCardModel
from database.models.user_model import UserModel
from database.session import get_session
from drops.card_drop_event import CardDropEvent
from drops.dropped_card import DroppedCard
from pokemon_tcg_loader import PokemonTCGLoader
from schemas.pokemon_card_schema import PokemonCardSchema
from database.managers.user_manager import UserNotExistError


class CardDropEventHandler:
    @staticmethod
    async def create_drop_event_random(card_amount: int, discord_message) -> CardDropEvent:
        random_tcg_cards = [PokemonTCGLoader.get_random_card() for _ in range(card_amount)]
        drop_event_id = str(uuid.uuid4()) 

        async with get_session() as session:
            drop_event_model = CardDropEventModel(
                id = drop_event_id,
                cards_dropped_ids=[tcg_card.id for tcg_card in random_tcg_cards],
                started_by_user_id = discord_message.author.id
            )
            session.add(drop_event_model)
            await session.commit()

        try:
            random_user_cards = await UserCardManager.create_cards_for_drop(random_tcg_cards, drop_event_id)
        except Exception as e:
            print(e)
            return None

        dropped_cards = []
        for x in range(len(random_user_cards)):
            dropped_cards.append(DroppedCard(random_tcg_cards[x], random_user_cards[x]))
            print(f"Creating Dropped card. TCG ID from PokemonCardSchema: {random_tcg_cards[x].id} TCG ID from UserCardModel: {random_user_cards[x].pokemon_tcg_card_id}")

        return CardDropEvent(drop_event_id, dropped_cards, discord_message)

    @staticmethod
    async def claim_card_at_index(drop_event: CardDropEvent, discord_user_id: int, card_index: int) -> DroppedCard:
        can_claim, error_message = CardDropEventHandler.can_user_claim_card(drop_event, discord_user_id, card_index)

        if not can_claim:
            raise InvalidClaimError(error_message)

        dropped_card = drop_event.dropped_cards[card_index]
        claimed_user_card = await UserCardManager.claim_card_id(discord_user_id, dropped_card.user_card.id)
        dropped_card.user_card = claimed_user_card

        drop_event.claimed_cards[card_index] = discord_user_id
        return dropped_card
    
    @staticmethod
    def can_user_claim_card(drop_event: CardDropEvent, user_discord_id: int, card_index: int) -> tuple[bool, str]:
        if drop_event.claimed_cards[card_index] is not None:
            return False, "This card has already been claimed."

        # Check if user has already claimed a card
        if user_discord_id in drop_event.claimed_cards:
            return False, "You have already claimed a card from this drop."

        # Owner can always interact (provided they haven't claimed one already)
        if user_discord_id == drop_event.owner_discord_id:
            return True, None
        
        # Check if Non-Owner time brace has expired
        timezone = pytz.timezone('UTC')  # Use UTC for consistency
        current_time = datetime.now(timezone)
        time_difference = current_time - drop_event.created_at
        owner_only = time_difference.total_seconds() <= drop_event.OWNER_ONLY_DURATION_SECONDS
        if owner_only:
            return False, f"You must wait at least {drop_event.OWNER_ONLY_DURATION_SECONDS} seconds to claim someone else's drop. Time left: {time_difference.total_seconds()} seconds"
        else:
            return True, None


class InvalidClaimError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        # You can customize the string representation of the error
        return f"Invalid Claim Error: {self.message}"
