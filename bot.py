import os
import discord
import logging
from bot_config import BotConfig
from discord_views.card_view import CardView
from discord_views.user_inventory_view import UserInventoryView
from drops.card_drop_event_handler import CardDropEventHandler
from database.managers.user_manager import UserManager
from pokemon_tcg_loader import PokemonTCGLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Bot Configuration and Data
discord_token = os.getenv('DISCORD_TOKEN')
PokemonTCGLoader.load_data()
BotConfig._load_config()

HELP_COMMAND = BotConfig.get("commands", "help")
DROP_COMMAND = BotConfig.get("commands", "drop")
INVENTORY_COMMAND = BotConfig.get("commands", "inventory")
VIEW_COMMAND = BotConfig.get("commands", "view")

# Set up logging
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log_handler.setLevel(logging.INFO)

# Define Bot Client
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

# Command Handlers
async def handle_help(message):
    help_message = f"""
    List of commands:
    `{DROP_COMMAND}` - Drop Cards
    `{INVENTORY_COMMAND}`  - Check all your cards
    `{VIEW_COMMAND}` - View a card. {VIEW_COMMAND} <card_id>
    """
    await message.channel.send(help_message)

async def handle_drop(message):
    await UserManager.get_or_create(message.author.id)
    can_drop, error_message = CardDropEventHandler.can_user_create_drop(message.author.id)

    if not can_drop:
        await message.channel.send(error_message)
        return

    drop_event = await CardDropEventHandler.create_drop_event_random(3, message)
    
    if drop_event:
        await drop_event.start()
    else:
        await message.channel.send(f"{message.author.mention} There was an error initiating your Drop. Try again later.")

async def handle_inventory(message):
    inventory_view = UserInventoryView(message.channel, message.author.id)
    await inventory_view.start()

async def handle_view(message, card_id: str):
    card = await UserManager.get_user_card(card_id)

    if card is None:
        await message.channel.send("Please double check the card ID.")
        return

    card_view = CardView(card, message.channel)
    await card_view.start()

# Event Handlers
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Handle help command
    if message.content == HELP_COMMAND:
        await handle_help(message)
        return

    # Handle drop command
    if message.content == DROP_COMMAND:
        await handle_drop(message)
        return

    # Handle inventory command
    if message.content == INVENTORY_COMMAND:
        await handle_inventory(message)
        return

    # Handle view command
    if message.content.startswith(VIEW_COMMAND):
        parts = message.content.split()

        if len(parts) == 2:
            card_id = parts[1]
            await handle_view(message, card_id)
        else:
            await message.channel.send("Please provide a valid card ID after the `!view` command.")
        return

# Run the bot
client.run(discord_token)
