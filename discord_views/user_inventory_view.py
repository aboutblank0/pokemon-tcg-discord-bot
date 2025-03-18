from enum import Enum
import discord

from pokemon_tcg_loader import PokemonTCGLoader
from database.managers.user_manager import UserManager
from utils.id_utils import to_base36


class UserInventoryView(discord.ui.View):
    CARDS_PER_PAGE = 10
    def __init__(self, discord_channel, discord_user_id: int):
        super().__init__(timeout=None)

        self.discord_channel = discord_channel
        self.discord_user_id = discord_user_id

        self.page_index = 0
        self.cursors = {}
        self.cursors[self.page_index] = 0


    async def start(self):
        cards, new_cursor, has_more = await UserManager.get_user_cards(self.discord_user_id, self.CARDS_PER_PAGE, self.cursors[self.page_index])
        self.cursors[1] = new_cursor

        self._refresh_items(has_more)

        embed = self._generate_inventory_embed(cards)
        self.discord_inventory_message = await self.discord_channel.send(embed=embed, view=self)

    async def navigate(self, direction):
        if direction == InventoryScrollDirection.BACK:
            self.page_index -= 1
        elif direction == InventoryScrollDirection.NEXT:
            self.page_index += 1

        cards, next_cursor, has_more = await UserManager.get_user_cards(self.discord_user_id, self.CARDS_PER_PAGE, self.cursors[self.page_index])
        if direction == InventoryScrollDirection.NEXT:
            self.cursors[self.page_index + 1] = next_cursor

        embed = self._generate_inventory_embed(cards)

        self._refresh_items(has_more)

        await self.discord_inventory_message.edit(embed=embed, view=self)

    def _generate_inventory_embed(self, cards):
        """Helper method to format card data and create an embed."""
        formatted_text = ""
        for card in cards:
            tcg_card = PokemonTCGLoader.load_card_data(card.pokemon_tcg_card_id)
            tcg_set = PokemonTCGLoader.load_set_data(tcg_card.set)

            formatted_text += f"`{to_base36(card.id)}`: {tcg_card.name} - **{tcg_set.name}** Float: `{card.float_value}` Pattern: `{card.pattern_number}`\n"

        embed = discord.Embed(
            title="🎴 Here is your Inventory!",
            description=f"Use the buttons to navigate to the next/previous pages. \n\n {formatted_text}",
            color=discord.Color.yellow()
        )

        return embed    
    
    def _refresh_items(self, has_more):
        self.clear_items()

        previous_button = InventoryPageNavigationButton(InventoryScrollDirection.BACK, self.page_index == 0)
        page_button = discord.ui.Button(label=str(self.page_index + 1), disabled=True)
        next_button = InventoryPageNavigationButton(InventoryScrollDirection.NEXT, not has_more)
        self.add_item(previous_button)
        self.add_item(page_button)
        self.add_item(next_button)


class InventoryPageNavigationButton(discord.ui.Button):

    PREVIOUS_EMOJI ='️⬅️' 
    NEXT_EMOJI = '➡️'

    def __init__(self, direction, disabled, *args, **kwargs):
        self.direction = direction

        label = self._get_direction_emoji(direction)
        super().__init__(label=label, style=discord.ButtonStyle.grey, disabled=disabled, *args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        await UserManager.get_or_create(interaction.user.id)
        await self.view.navigate(self.direction)
        await interaction.response.defer()
    
    def _get_direction_emoji(self, direction):
        if direction == InventoryScrollDirection.BACK:
            return self.PREVIOUS_EMOJI
        elif direction == InventoryScrollDirection.NEXT:
            return self.NEXT_EMOJI

class InventoryScrollDirection(Enum):
    BACK = 1
    NEXT = 2