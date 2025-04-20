import discord
import os
from random import Random
from dotenv import load_dotenv
import sqlite3

load_dotenv()
token = os.getenv('DISCORD_TOKEN')


random = Random()


sql_connection = sqlite3.connect("game.db")
cursor = sql_connection.cursor()

def get_player_table():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
    return cursor.fetchall()

def create_tables():
    cursor.execute("CREATE TABLE players(id)")
    cursor.execute("CREATE TABLE game_state(channel, accepting_new_players, player_list)")
    cursor.execute("CREATE TABLE memberships(player_id, channel_id)")
    return cursor.fetchall()

def player_exists_in_db(player):
    cursor.execute("SELECT * FROM players WHERE name = ?", (player,))
    return cursor.fetchall()

def create_player_in_db(player):
    cursor.execute("INSERT INTO players VALUES (?)", (player,))
    return cursor.fetchall()

def new_game(channel):
    cursor.execute("INSERT INTO game_state(channel, accepting_new_players) VALUES (?, ?)", (channel, True))
    return cursor.fetchall()

def join_game(player, channel):
    cursor.execute("INSERT INTO memberships(player_id, channel_id) VALUES (?, ?)", (player, channel))
    return cursor.fetchall()

def start_game(channel):
    cursor.execute("UPDATE game_state SET accepting_new_players = ? WHERE channel = ?", (False, channel))
    return cursor.fetchall()

def get_game_state(channel):
    cursor.execute("SELECT * FROM game_state WHERE channel = ?", (channel,))
    return cursor.fetchall()

def player_is_joined(player, channel):
    cursor.execute("SELECT * FROM memberships WHERE player_id = ? AND channel_id = ?", (player, channel))
    return cursor.fetchall()

def game_is_accepting_players(channel):
    cursor.execute("SELECT * FROM channels WHERE channel = ? AND accepting_new_players = ?", (channel, True))
    return cursor.fetchall()


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        if not get_player_table():
            create_tables()

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return
        channel = self.get_channel(message.channel.id)
        game_state = get_game_state(channel.id)
        if not game_state and message.content.startswith('!new'):
            await channel.send(f'New game in channel {message.channel}')
            new_game(channel.id)
        if game_state and game_is_accepting_players(channel.id) and not player_is_joined(message.author.id, channel.id) and message.content.startswith('!join'):
            await channel.send(f'Player {message.author} joined game in channel {message.channel}')
            join_game(message.author.id, channel.id)
        if game_state and message.content.startswith('!start'):
            await channel.send(f'Game in channel {message.channel} has started')
            start_game(channel.id)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents, activity=discord.Game(name='Cuck Simulator 🕺'))
client.run(token)
