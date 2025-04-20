# Discord Card Game Bot

A Discord bot that implements a card game system with deck management and multiplayer functionality.

## Features

- Create new game sessions in Discord channels
- Join existing game sessions
- Start games with multiple players
- Persistent player decks using SQLite database
- Card management system with rarity and color attributes

## Prerequisites

- Python 3.8 or higher
- Discord.py 2.5.2
- SQLite3
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
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

The bot responds to the following commands:

- `!new` - Creates a new game in the current channel
- `!join` - Joins the current game in the channel
- `!start` - Starts the game with all joined players

## Project Structure

```
.
├── src/
│   ├── main.py         # Main bot implementation
│   └── game.db         # SQLite database for player data
├── data/
│   ├── cards.csv       # Card definitions
│   └── basic_deck.csv  # Default deck configuration
├── requirements.txt    # Project dependencies
└── .env               # Environment variables
```

## Database Schema

The bot uses SQLite to store player data:
- `players` table: Stores player IDs and their deck configurations

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your chosen license]

## Acknowledgments

- Discord.py for the Discord API wrapper
- SQLite for the database backend