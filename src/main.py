import csv
import os
import sqlite3
from random import Random

import discord
from discord import Client
from discord.app_commands import CommandTree
from dotenv import load_dotenv

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../data/"

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

if token is None:
    print("DISCORD_TOKEN env not set")
    exit()

random = Random()

game_state = {
    "cards": {},
    "games": {},
}
with open(DATA_DIR + "cards.csv", newline="") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        game_state["cards"][row[0]] = {
            "rarity": row[1],
            "color": row[2],
            "value": row[3],
        }

basic_deck = []
with open(DATA_DIR + "basic_deck.csv", newline="") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        basic_deck.append(row[0])


def new_game(channel):
    if not channel.id in game_state:
        game_state["games"][channel.id] = {"status": "open", "players": {}}
        return True
    return False


def join_game(player, channel):
    game = game_state["games"][channel.id]
    game_is_open = game["status"] == "open"
    player_is_joined = player.id in game["players"]
    if game_is_open and not player_is_joined:
        starting_deck = get_player_starting_deck(player)
        hand = starting_deck[0:7]
        deck = starting_deck[7:]
        game_state["games"][channel.id]["players"][player.id] = {
            "name": player.name,
            "deck": deck,
            "hand": hand,
        }
        return True
    return False


def start_game(channel):
    game = game_state["games"][channel.id]
    game_is_open = game["status"] == "open"
    lobby_size = len(game["players"])
    if game_is_open and lobby_size > 0:
        game_state["games"][channel.id]["status"] = "closed"
        return True
    return False


def serialize_cards(cards):
    return ",".join(cards)


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
    return cursor.fetchall()


def create_player_in_db(player, deck):
    deck = ",".join(deck)
    cursor.execute("INSERT INTO players VALUES (?, ?)", (player.id, deck))
    return cursor.fetchall()


def get_player_starting_deck(player):
    cursor.execute("SELECT deck FROM players WHERE id = ?", (player.id,))
    return cursor.fetchall()[0][0].split(",")


intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents, activity=discord.Game(name="Cuck Simulator 🕺"))
tree = CommandTree(client)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.content.startswith("!register"):
        await tree.sync()
        await message.channel.send("registering commands")


@tree.command(name="ping", description="ping")
async def ping(interaction):
    await interaction.response.send_message("pong")


@tree.command(name="new", description="Create new game")
async def new(interaction):
    channel = interaction.channel
    if new_game(channel):
        await interaction.response.send_message(f"New game in channel {channel}")


@tree.command(
    name="join",
    description="join a game",
)
async def join(interaction):
    (channel, player) = (interaction.channel, interaction.player)
    if interaction.user == client.user:
        return

    if interaction.user == client.user:
        return
    if not player_exists_in_db(player):
        create_player_in_db(player, serialize_cards(basic_deck))
    if join_game(player, channel):
        await interaction.response.send_message(
            f"Player {player} joined game in channel {channel}"
        )


@tree.command(name="start", description="start a game")
async def start(interaction):
    channel = interaction.channel
    if start_game(channel):
        await interaction.response.send_message(
            f"Game in channel {channel} has started"
        )


client.run(token)
