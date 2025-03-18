from datetime import datetime, timedelta
import uuid
import pytz
from bot_config import BotConfig
from database.managers.user_card_manager import UserCardManager
from database.models.card_drop_event_model import CardDropEventModel
from database.session import get_session
from drops.card_drop_event import CardDropEvent
from drops.dropped_card import DroppedCard
from pokemon_tcg_loader import PokemonTCGLoader


class CardDropEventHandler:
    DROP_COOLDOWN_SECONDS = BotConfig.get_int("drop_event", "user_start_cooldown_seconds")
    CLAIM_COOLDOWN_SECONDS = BotConfig.get_int("drop_event", "user_claim_cooldown_seconds")

    last_drop_time = {}
    last_claim_time = {}

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

        CardDropEventHandler.last_drop_time[discord_message.author.id] = datetime.now() 
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
        CardDropEventHandler.last_claim_time[discord_user_id] = datetime.now() 
        return dropped_card
    
    @staticmethod
    def can_user_claim_card(drop_event: CardDropEvent, discord_user_id: int, card_index: int) -> tuple[bool, str]:
        if discord_user_id in CardDropEventHandler.last_claim_time:
            current_time = datetime.now()
            last_user_time = CardDropEventHandler.last_claim_time[discord_user_id] 
            time_diff = current_time - last_user_time

            # Check if the user is still under cooldown
            if time_diff < timedelta(seconds=CardDropEventHandler.CLAIM_COOLDOWN_SECONDS):
                time_left = timedelta(seconds=CardDropEventHandler.CLAIM_COOLDOWN_SECONDS) - time_diff
                return False, f"You must wait {CardDropEventHandler._format_time_left(time_left)} before claiming more cards"

        if drop_event.claimed_cards[card_index] is not None:
            return False, "This card has already been claimed."

        # Check if user has already claimed a card
        if discord_user_id in drop_event.claimed_cards:
            return False, "You have already claimed a card from this drop."

        # Owner can always interact (provided they haven't claimed one already)
        if discord_user_id == drop_event.owner_discord_id:
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

    @staticmethod
    def can_user_create_drop(discord_user_id: int):
        if discord_user_id in CardDropEventHandler.last_drop_time:
            current_time = datetime.now()
            last_user_time = CardDropEventHandler.last_drop_time[discord_user_id] 
            time_diff = current_time - last_user_time

            # Check if the user is still under cooldown
            if time_diff < timedelta(seconds=CardDropEventHandler.DROP_COOLDOWN_SECONDS):
                time_left = timedelta(seconds=CardDropEventHandler.DROP_COOLDOWN_SECONDS) - time_diff
                return False, f"<@{discord_user_id}>, You must wait {CardDropEventHandler._format_time_left(time_left)} before dropping more cards"

            else:
                return True, None
        
        else:
            return True, None
    
    def _format_time_left(time_left: timedelta):
        time_left_seconds = time_left.total_seconds()
        
        hours = int(time_left_seconds // 3600)
        minutes = int((time_left_seconds % 3600) // 60)
        seconds = int(time_left_seconds % 60)
        
        # If there's more than 1 hour, show hours, minutes, and seconds
        if hours > 0:
            return f"`{hours} hour{'s' if hours > 1 else ''}, {minutes} minute{'s' if minutes > 1 else ''}, {seconds} second{'s' if seconds != 1 else ''}`"
        
        # If there's more than 1 minute but less than an hour, show minutes and seconds
        elif minutes > 0:
            return f"`{minutes} minute{'s' if minutes > 1 else ''}, {seconds} second{'s' if seconds != 1 else ''}`"
        
        # Otherwise, just show seconds
        else:
            return f"`{seconds} second{'s' if seconds != 1 else ''}`"
    


class InvalidClaimError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        # You can customize the string representation of the error
        return f"Invalid Claim Error: {self.message}"
