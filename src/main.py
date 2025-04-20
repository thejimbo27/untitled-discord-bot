import discord
import os
from random import Random
from dotenv import load_dotenv
import sqlite3
import csv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')


random = Random()


game_state = {
    "cards": {},
}
with open('../data/cards.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        game_state["cards"][row[0]] = {
            "rarity": row[1],
            "color": row[2],
            "value": row[3],
        }

starting_deck = []
with open('../data/starting_deck.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        starting_deck.append(row[0])

def new_game(channel):
    if not channel.id in game_state:
        game_state[channel.id] = {
            "status": "open",
            "players": {}
        }
        return True
    return False

def join_game(player, channel):
    game_is_open = game_state[channel.id]["status"] == "open"
    player_is_joined = player.id in game_state[channel.id]["players"]
    if game_is_open and not player_is_joined:
        starting_deck = get_player_starting_deck(player)
        hand = starting_deck[0:7]
        deck = starting_deck[7:]
        game_state[channel.id]["players"][player.id] = {
            "deck": deck,
            "hand": hand
        }
        return True
    return False

def start_game(channel):
    game_is_open = game_state[channel.id]["status"] == "open"
    lobby_size = len(game_state[channel.id]["players"])
    if game_is_open and lobby_size > 0:
        game_state[channel.id]["status"] = "closed"
        for player in game_state[channel.id]["players"]:
            channel.send(f"{player}'s deck: {player["deck"]}")
            channel.send(f"{player}'s hand: {player["hand"]}")
        return True
    return False


def serialize_cards(cards):
    return ",".join(cards)

def deserialize_cards(cards):
    return cards.split(",")


sql_connection = sqlite3.connect("game.db")
cursor = sql_connection.cursor()

def get_player_table():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
    return cursor.fetchall()

def create_tables():
    cursor.execute("CREATE TABLE players(id, deck)")
    return cursor.fetchall()

def player_exists_in_db(player):
    cursor.execute("SELECT * FROM players WHERE id = ?", (player.id,))
    return cursor.fetchall()

def create_player_in_db(player, deck):
    cursor.execute("INSERT INTO players VALUES (?, ?)", (player.id, deck))
    return cursor.fetchall()

def get_player_starting_deck(player):
    cursor.execute("SELECT deck FROM players WHERE id = ?", (player.id,))
    deck = deserialize_cards(cursor.fetchall()[0])
    return deck


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        if not get_player_table():
            create_tables()

    async def on_message(self, message):
        if message.author == self.user:
            return
        player = message.author
        channel = message.channel
        if not player_exists_in_db(player):
            create_player_in_db(player, serialize_cards(starting_deck))
        print(f'Message from {player}: {message.content}')
        if message.content.startswith('!new'):
            if new_game(channel):
                await channel.send(f'New game in channel {channel}')
        if message.content.startswith('!join'):
            if join_game(player, channel):
                await channel.send(f'Player {player} joined game in channel {channel}')
        if message.content.startswith('!start'):
            if start_game(channel):
                await channel.send(f'Game in channel {channel} has started')


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents, activity=discord.Game(name='Cuck Simulator 🕺'))
client.run(token)
