import csv
import os
import sqlite3
from random import Random

import discord
from discord import Client
from discord.app_commands import CommandTree
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
            "value": row[3],
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
            "active_card": {},
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
    if card_id not in game["players"][player.id]["hand"] or player.id != game["initiative"][0]:
        return False
    game_state[channel.id]["active_card"] = all_cards[card_id]
    game_state[channel.id]["players"][player.id]["hand"].remove(card_id)
    game_state[channel.id]["initiative"] = game_state[channel.id]["initiative"][1:] + game_state[channel.id][
                                                                                          "initiative"][:1]
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


@tree.command(name="ping", description="ping")
async def ping(interaction):
    await interaction.response.send_message("pong")


@tree.command()
async def new(interaction):
    """Start a new game"""
    channel = interaction.channel
    if new_game(channel):
        await interaction.response.send_message(f"New game in channel {channel}")


@tree.command()
async def join(interaction):
    """Join a game"""
    (channel, player) = (interaction.channel, interaction.user)
    if interaction.user == client.user:
        return

    if not player_exists_in_db(player):
        create_player_in_db(player, basic_deck)
    if join_game(player, channel):
        response = 'You have the following cards in your hand:'
        for card_id in game_state[interaction.channel.id]["players"][interaction.user.id]["hand"]:
            response += f"\n[{card_id}] {all_cards[card_id]["name"]}"
        await interaction.response.send_message(response, ephemeral=True)


@tree.command()
async def play(interaction, card_id: str):
    """This command plays a card from your hand.

    Parameters
    -----------
    card_id: str
        The ID of the card to play.
    """

    (channel, player) = (interaction.channel, interaction.user)
    if play_card(player, channel, card_id):
        next_player_id = game_state[channel.id]["initiative"][0]
        next_player_name = game_state[channel.id]["players"][next_player_id]["name"]
        response = f"{player.name} played {all_cards[card_id]['name']}"
        response += f"\n{next_player_name}, it is your turn."
        await interaction.response.send_message(response)


@tree.command()
async def start(interaction):
    """Start game"""
    channel = interaction.channel
    if start_game(channel):
        response = f"Game in channel {channel} has started"
        player_id = game_state[channel.id]["initiative"][0]
        player_name = game_state[channel.id]["players"][player_id]["name"]
        response += f"\n{player_name}, it is your turn."
        await interaction.response.send_message(response)


client.run(token)
