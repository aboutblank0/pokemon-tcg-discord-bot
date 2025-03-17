from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user_card_model import UserCardModel
from database.models.user_model import UserModel
from database.session import get_session
from utils.id_utils import from_base36

class UserManager:

    @staticmethod
    async def get_or_create(discord_user_id: int) -> UserModel:
        async with get_session() as session:
            # Use session.get for direct retrieval by primary key (discord_user_id)
            db_user = await session.get(UserModel, discord_user_id)

            if db_user:
                # User exists, return the existing user
                return db_user

            # If user does not exist, create a new user
            new_user = UserModel(discord_user_id=discord_user_id)
            session.add(new_user)
            await session.commit()
            
            return new_user

    @staticmethod
    async def get_all_user_cards(discord_user_id: int) -> list[UserCardModel]:
        """
        Returns all cards for the given user.
        """
        async with get_session() as session:
            query = select(UserCardModel).filter(UserCardModel.owner_id == discord_user_id)

            result = await session.execute(query)
            user_cards = result.scalars().all()

            return user_cards 

    @staticmethod
    async def get_user_cards(discord_user_id: int, amount: int, cursor: int = None):
        """
        Returns X amount of cards that the user has, paginated by cursor.
        Also returns whether there are more cards after the returned set.
        """
        async with get_session() as session:
            query = select(UserCardModel).filter(UserCardModel.owner_id == discord_user_id)
            
            # If cursor is provided, filter by cards with id greater than the cursor value (for pagination)
            if cursor:
                query = query.filter(UserCardModel.id > cursor)
            
            query = query.limit(amount + 1)  # Fetch one extra card to check for more
            result = await session.execute(query)
            user_cards = result.scalars().all()

            has_more = len(user_cards) > amount  # If we got more than `amount`, there's more data
            
            if has_more:
                user_cards = user_cards[:amount]  # Trim to the requested amount
            
            # If there are results, return the cards, the last card's ID, and `has_more`
            if user_cards:
                return user_cards, user_cards[-1].id, has_more

            return [], None, False  # No cards found, return empty list, None cursor, and False for `has_more`


    @staticmethod
    async def get_user_card(base_36_id: str) -> UserCardModel:
        """
        Returns all cards for the given user.
        """
        real_card_id = from_base36(base_36_id)

        async with get_session() as session:
            card = await session.get(UserCardModel, real_card_id)
            return card

class UserNotExistError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        # You can customize the string representation of the error
        return f"User Not Exist: {self.message}"

    
