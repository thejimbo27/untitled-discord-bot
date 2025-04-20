import discord
import os
from random import Random
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')


random = Random()



class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return
        channel = self.get_channel(1363384148227784755)
        msg = random.randint(1,6)
        if msg == 1:
            await channel.send('you look cute v.v')
        if msg == 2:
            await channel.send('nice cock !')
        if msg == 3:
            await channel.send('put a girl on >.>')
        if msg == 4:
            await channel.send('thank you !!  can i see ur muscles x_x')
        if msg == 5:
            await channel.send('Kill yourself.')
        if msg == 6:
            await channel.send('initiating beeper mashing.')


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents, activity=discord.Game(name='Cuck Simulator 🕺'))
client.run(token)
