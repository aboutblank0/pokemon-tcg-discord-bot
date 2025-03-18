# Pokemon Trading Card Discord Bot

Discord bot where you can collect pokemon cards. Heavily inspired by the already existing [Karuta Discord Bot](https://karuta.com/).

I decided to put a very simple "twist" on it; each card that is dropped gets a random "float_value" and "pattern_number" which determine its appearance(how damaged it looks) which adds an extra layer of "RNG" which makes it more fun. This is seeded using the id of the Pokemon TCG Card, so a card of two different pokemon with the same pattern_number and float_value will look different.

There are a million improvements/features/bug-fixes I could do but I am ready to let go of this project as I am happy with its state after ~1 week.

## Showcase

### Card drop:

<img src="images/drop.png" height="300" style="width:auto;">

### Viewing a "high float" card:

<img src="images/view.png" height="300" style="width:auto;">

### Viewing inventory:

<img src="images/inventory.png" height="300" style="width:auto;">

### Features

- Float and Pattern number modifying cards appearance
- Print number for each card (depending on tcg id)
- Drop 3 cards on a cooldown per user
- User claiming cooldown
- Persistent inventory
- Configurable by modifying `bot_config.ini`

## Setup / Installation

Follow these steps to set up the project:

### 1. Clone the repository:

```bash
git clone https://github.com/aboutBlank-dev/pokemon-tcg-discord-bot.git
cd pokemon-tcg-discord-bot
```

### 2. Set up and activate the Python virtual environment:

**For Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**For Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies:

With the virtual environment activated, install the project dependencies by running:

```bash
pip install -r requirements.txt
```

### 4. Set up Local Postgres DB with Docker (Or do it your way)

Make sure you have [Docker](https://www.docker.com/) installed and running then execute the following commands:

```bash
docker pull postgres
docker create --name <your-container-name> -e POSTGRES_USER=<your-db-user> -e POSTGRES_PASSWORD=<your-db-password> -e POSTGRES_DB=<your-db> -p 5432:5432 postgres
```

Replace `<your-container-name>`,`<your-db-user>`, `<your-db-password>`, `<your-db>` with your own custom values. Remember these as they are needed for the next step.

After successfully creating the container, you can start/stop it using the following commands:

```bash
docker start <your-container-name>
docker stop <your-container-name>
```

**Note**: The container will have to be running whenever you want to run the Bot.

### 5. Set up the `.env` file:

Create a .env file with the following:

```ini
DISCORD_TOKEN=your-discord-bot-token
DATABASE_URL=your-postgresql-async-url
DATABASE_URL_ALEMBIC=your-postgresql-url
POKEMON_TCG_API_KEY=your-pokemon-tcg-api-key
```

- **DISCORD_TOKEN**: [Discord developer Portal](https://discord.com/developers/applications). Further help: [Click me](https://discord.com/developers/docs/quick-start/getting-started#step-1-creating-an-app)
- **POKEMON_TCG_API_KEY**: Sign up to [Pokemon TCG Developer Portal](https://dev.pokemontcg.io/) to get your _FREE_ API Key
- **DATABASE_URL**: `postgresql+asyncpg://<your-db-user>:<your-db-password>@localhost/<your-db>`
- **DATABASE_URL_ALEMBIC**: `postgresql://<your-db-user>:<your-db-password>@localhost/<your-db>`

Use the values from the previous step (Set up local Postgres DB with Docker) to replace `<your-db-user>`, `<your-db-password>`, and `<your-db>`."

### 6. Run Db migrations using alembic

Make sure the virtual environment is activated and run this command in the **root** of the project:

```bash
alembic upgrade head
```

### 7. Run Pokemon TCG SDK saver script

Download & Save the data for every card in the SDK. _(WARNING: This will take a long time (~15 minutes) and take up ~2GBs of space)_

```bash
python .scripts/pokemon_tcg_saver.py
```

### 8. Start the bot

After everything is set up, make sure your docker container/database is running and run the following command:

```bash
python bot.py
```
