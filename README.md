# Discord Card Game Bot

A Discord bot that implements a UNO-style card game with deck management and multiplayer functionality.

## Features

- Create and manage game sessions in Discord channels
- Join existing game sessions
- Start games with multiple players
- Persistent player decks using SQLite database
- Card management system with:
  - Four colors (red, yellow, green, blue)
  - Number cards (0-9)
  - Special cards (skip, reverse, draw2)
- Real-time game state tracking
- Player hand management
- Turn-based gameplay

## Prerequisites

- Python 3.8 or higher
- Discord.py 2.5.2
- SQLite3
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/thejimbo27/untitled-discord-bot.git
cd untitled-discord-bot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Discord bot token:
```
DISCORD_TOKEN=your_bot_token_here
```

## Usage

The bot responds to the following slash commands:

- `/new` - Creates a new game in the current channel
- `/join` - Joins the current game in the channel
- `/start` - Starts the game with all joined players
- `/play [card_id]` - Plays a card from your hand
- `/draw` - Draws a card from your deck
- `/hand` - Views your current hand
- `/ping` - Checks if the bot is responsive

## Project Structure

```
.
├── src/
│   ├── main.py         # Main bot implementation
│   ├── views.py        # Discord UI components
│   └── game.db         # SQLite database for player data
├── data/
│   ├── cards.csv       # Card definitions (ID, rarity, color, face, name)
│   └── basic_deck.csv  # Default deck configuration
├── requirements.txt    # Project dependencies
└── .env               # Environment variables
```

## Database Schema

The bot uses SQLite to store player data:
- `players` table: Stores player IDs and their deck configurations

## Card System

The game includes:
- Number cards (0-9) in four colors
- Special cards:
  - Skip: Skips the next player's turn
  - Reverse: Reverses the turn order
  - Draw 2: Makes the next player draw two cards

## Contributing

#420Hackaton
Jimbo
Scoopahdoopah
riotctrl

## License

[Your chosen license]

## Acknowledgments

- Discord.py for the Discord API wrapper
- SQLite for the database backend