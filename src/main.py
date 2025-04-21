import csv
import os
import sqlite3
from functools import partial
from random import Random

import discord
from discord import Client
from discord.app_commands import CommandTree
from discord.ui import Button, View
from dotenv import load_dotenv


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

if token is None:
    print("DISCORD_TOKEN env not set")
    exit()

random = Random()

game_state = {}
all_cards = {}
with open("data/cards.csv", newline="") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        all_cards[row[0]] = {
            "rarity": row[1],
            "color": row[2],
            "face": row[3],
            "name": row[4],
        }

basic_deck = []
with open("data/basic_deck.csv", newline="") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        basic_deck.append(row[0])


def new_game(channel):
    if not channel.id in game_state:
        game_state[channel.id] = {
            "status": "open",
            "players": {},
            "initiative": [],
            "active_card": {
                "rarity": None,
                "color": None,
                "face": None,
                "name": None,
            },
        }
        return True
    return False


def join_game(player, channel):
    game = game_state[channel.id]
    game_is_open = game["status"] == "open"
    player_is_joined = player.id in game["players"]
    if game_is_open and not player_is_joined:
        starting_deck = get_player_starting_deck(player)
        random.shuffle(starting_deck)
        hand = starting_deck[0:7]
        deck = starting_deck[7:]
        game_state[channel.id]["players"][player.id] = {
            "name": player.name,
            "deck": deck,
            "hand": hand,
        }
        game_state[channel.id]["initiative"].append(player.id)
        return True
    return False


def start_game(channel):
    game = game_state[channel.id]
    game_is_open = game["status"] == "open"
    lobby_size = len(game["players"])
    if game_is_open and lobby_size > 0:
        game_state[channel.id]["status"] = "closed"
        return True
    return False


def play_card(player, channel, card_id):
    game = game_state[channel.id]
    try:
        card = all_cards[card_id]
    except KeyError:
        return False
    if card_id not in game["players"][player.id]["hand"] or player.id != game["initiative"][0] or game["status"] == "open":
        return False
    if game["active_card"]["name"] == None:
        game_state[channel.id]["active_card"] = card
    if card["color"] == "wild":
        card["color"] = game_state[channel.id]["active_card"]["color"]
    if card["face"] == "wild":
        card["face"] = game_state[channel.id]["active_card"]["face"]
    if card["face"] == "skip":
        if game["active_card"]["color"] != card["color"] and game["active_card"]["face"] != card["face"]:
            return False
        game_state[channel.id]["players"][player.id]["hand"].remove(card_id)
        game_state[channel.id]["active_card"] = card
        game_state[channel.id]["initiative"] = game_state[channel.id]["initiative"][-1:] + game_state[channel.id]["initiative"][:-1]
        game_state[channel.id]["initiative"] = game_state[channel.id]["initiative"][-1:] + game_state[channel.id]["initiative"][:-1]
    if card["face"] == "reverse":
        if game["active_card"]["color"] != card["color"] and game["active_card"]["face"] != card["face"]:
            return False
        game_state[channel.id]["players"][player.id]["hand"].remove(card_id)
        game_state[channel.id]["active_card"] = card
        game_state[channel.id]["initiative"] = game_state[channel.id]["initiative"][::-1]
    if card["face"] == "draw2":
        if game["active_card"]["color"] != card["color"] and game["active_card"]["face"] != card["face"]:
            return False
        game_state[channel.id]["players"][player.id]["hand"].remove(card_id)
        game_state[channel.id]["active_card"] = card
        next_player = game_state[channel.id]["initiative"][1]
        game_state[channel.id]["players"][next_player]["hand"].append(game_state[channel.id]["players"][next_player]["deck"].pop(0))
        game_state[channel.id]["players"][next_player]["hand"].append(game_state[channel.id]["players"][next_player]["deck"].pop(0))
        game_state[channel.id]["initiative"] = game_state[channel.id]["initiative"][-1:] + game_state[channel.id]["initiative"][:-1]
    if card["face"] == "draw4":
        next_player = game_state[channel.id]["initiative"][1]
        game_state[channel.id]["active_card"] = card
        game_state[channel.id]["players"][next_player]["hand"].append(game_state[channel.id]["players"][next_player]["deck"].pop(0))
        game_state[channel.id]["players"][next_player]["hand"].append(game_state[channel.id]["players"][next_player]["deck"].pop(0))
        game_state[channel.id]["players"][next_player]["hand"].append(game_state[channel.id]["players"][next_player]["deck"].pop(0))
        game_state[channel.id]["players"][next_player]["hand"].append(game_state[channel.id]["players"][next_player]["deck"].pop(0))
        game_state[channel.id]["initiative"] = game_state[channel.id]["initiative"][-1:] + game_state[channel.id]["initiative"][:-1]
        game_state[channel.id]["initiative"] = game_state[channel.id]["initiative"][-1:] + game_state[channel.id]["initiative"][:-1]
    else:
        if game["active_card"]["color"] != card["color"] and game["active_card"]["face"] != card["face"]:
            return False
        game_state[channel.id]["players"][player.id]["hand"].remove(card_id)
        game_state[channel.id]["active_card"] = card
        game_state[channel.id]["initiative"] = game_state[channel.id]["initiative"][-1:] + game_state[channel.id]["initiative"][:-1]
    return True


def draw_card(player, channel):
    game = game_state[channel.id]
    if player.id != game["initiative"][0] or game["status"] == "open":
        return False
    game_state[channel.id]["players"][player.id]["hand"].append(
        game_state[channel.id]["players"][player.id]["deck"].pop(0))
    return True


def serialize_cards(cards):
    return ",".join(cards)


def deserialize_cards(cards):
    return cards[0][0].split(",")


sql_connection = sqlite3.connect("game.db")
cursor = sql_connection.cursor()


def get_player_table():
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='players'"
    )
    return cursor.fetchall()


def create_tables():
    cursor.execute("CREATE TABLE players(id, deck)")
    return cursor.fetchall()


def player_exists_in_db(player):
    cursor.execute("SELECT * FROM players WHERE id = ?", (player.id,))
    return cursor.fetchone() is not None


def create_player_in_db(player, deck):
    cursor.execute("INSERT INTO players VALUES (?, ?)", (player.id, serialize_cards(deck)))
    return cursor.fetchall()


def get_player_starting_deck(player):
    cursor.execute("SELECT deck FROM players WHERE id = ?", (player.id,))
    return deserialize_cards(cursor.fetchall())


error_messages = [
    "sum ting wong",
    "wi tu lo",
    "ho lee fuk",
    "bang ding ow",
]


intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents, activity=discord.Game(name="Cuck Simulator 🕺"))
tree = CommandTree(client)


@client.event
async def on_ready():
    if not get_player_table():
        create_tables()
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.content.startswith("!register"):
        await tree.sync()
        await message.channel.send("registering commands")


@tree.command()
async def ping(interaction):
    """Ping the bot to check if it's alive"""
    await interaction.response.send_message("pong")


@tree.command()
async def help(interaction):
    """Get help about available commands and how to play"""
    help_message = """**🎮 Card Game Bot Commands**

**Game Setup:**
`/new` - Create a new game in the current channel
`/join` - Join the current game in the channel
`/start` - Start the game with all joined players

**Gameplay:**
`/play` - Play a card from your hand
`/draw` - Draw a card from your deck
`/hand` - View your current hand

**Other:**
`/ping` - Check if the bot is responsive
`/help` - Show this help message

**How to Play:**
1. Use `/new` to create a game
2. Have other players join with `/join`
3. Start the game with `/start`
4. Players take turns playing cards that match either the color or number of the last played card
5. Special cards:
   - Skip: Skips the next player's turn
   - Reverse: Reverses the turn order
   - Draw 2: Makes the next player draw two cards
6. Use `/draw` if you can't play any cards
7. First player to empty their hand wins!

For more information, check out the [GitHub repository](https://github.com/thejimbo27/untitled-discord-bot)."""
    
    await interaction.response.send_message(help_message)


@tree.command()
async def new(interaction):
    """Start a new game"""
    channel = interaction.channel
    if new_game(channel):
        await interaction.response.send_message(f"New game in channel {channel}")
    else:
        await interaction.response.send_message(random.choice(error_messages), ephemeral=True)


@tree.command()
async def join(interaction):
    """Join a game"""
    (channel, player) = (interaction.channel, interaction.user)
    if interaction.user == client.user:
        return

    if not player_exists_in_db(player):
        create_player_in_db(player, basic_deck)
    if join_game(player, channel):
        response = f"{player.name} joined the game!"
        await interaction.response.send_message(response)
    else:
        await interaction.response.send_message(random.choice(error_messages), ephemeral=True)


@tree.command()
async def play(interaction):
    """This command plays a card from your hand."""
    channel = interaction.channel
    response = f"Last played: {game_state[channel.id]["active_card"]["name"]}"
    for player in game_state[channel.id]["players"]:
        player_name = game_state[channel.id]["players"][player]["name"]
        num_of_cards = len(game_state[channel.id]["players"][player]["hand"])
        response += f"\n{player_name} has {num_of_cards} cards in their hand."
    await interaction.response.send_message(response, view=PlayView(interaction), ephemeral=True)


@tree.command()
async def start(interaction):
    """Start a game"""
    channel = interaction.channel
    if start_game(channel):
        response = f"Game in channel {channel} has started"
        player_id = game_state[channel.id]["initiative"][0]
        response += f"\n<@{player_id}>, it is your turn."
        await interaction.response.send_message(response)
    else:
        await interaction.response.send_message(random.choice(error_messages), ephemeral=True)


class PlayView(View):
    def __init__(self, interaction):
        super().__init__()

        async def card_cb(interaction, cid):
            (channel, player) = (interaction.channel, interaction.user)
            if play_card(player, channel, cid):
                next_player_id = game_state[channel.id]["initiative"][0]
                send = f"{player.name} played {all_cards[cid]['name']}"
                send += f"\n<@{next_player_id}>, it is your turn."
                await channel.send(send)
                await interaction.response.edit_message(content=f"You played {all_cards[cid]['name']}", view=None,
                                                        delete_after=3)
            else:
                await interaction.response.send_message(random.choice(error_messages), ephemeral=True)

        for card_id in game_state[interaction.channel.id]["players"][interaction.user.id]["hand"]:
            button = Button(label=f'{all_cards[card_id]["name"]}')
            button.callback = partial(card_cb, cid=card_id)
            self.add_item(button)

        async def draw_cb(interaction):
            (channel, player) = (interaction.channel, interaction.user)
            if draw_card(player, channel):
                send = f"{player.name} drew a card."
                await channel.send(send)
                response = f'Last played: {game_state[channel.id]["active_card"]["name"]}'
                for player in game_state[channel.id]["players"]:
                    num_cards_in_hand = len(game_state[channel.id]["players"][player]["hand"])
                    player_name = game_state[channel.id]["players"][player]["name"]
                    response += f"\n{player_name} has {num_cards_in_hand} cards in their hand"
                await interaction.response.edit_message(content=response, view=PlayView(interaction))
            else:
                await interaction.response.send_message(random.choice(error_messages), ephemeral=True)

        draw_button = Button(label=f'draw')
        draw_button.callback = draw_cb
        self.add_item(draw_button)


client.run(token)