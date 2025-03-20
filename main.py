import discord
from discord.ext import commands
import json
import os
import zipfile

# Lire le fichier JSON
with open('link.json', 'r') as json_file:
    link_data = json.load(json_file)


intents = discord.Intents.default()
intents.messages = True
intents.message_content  = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("ready")

@client.event
async def on_message(message):
    global link_data
    if message.author == client.user:
        return

    if message.content.lower().startswith("!"): 
        try:
            # Construit le chemin vers le fichier
            file_path = "v_list/" + link_data[message.content.lower()[1:]]["file"]
            
            await message.channel.send(file=discord.File(file_path))
        except Exception as e:
            await message.channel.send(f"Le serveur `{message.content.lower()[1:]}` n'existe pas ou le fichier est introuvable.")
    elif message.content.lower().startswith("€"):
        file_name = "v_list/" + message.content.lower()[1:]+".zip"
        if not os.path.exists(file_name):
            with open(file_name, 'w') as fichier:
                if os.path.exists('link.json'):
                    with open('link.json', 'r') as json_file:
                        link_data = json.load(json_file)
                else:
                    link_data = {}
                link_data[message.content.lower()[1:]] = {
                        "file": "v_list"+message.content.lower()[1:]+".zip",
                        "maker": message.author.name
                }
                with open('link.json', 'w') as json_file:
                    json.dump(link_data, json_file, indent=4)
                for attachment in message.attachments:
                    temp_file_name = attachment.filename
                    await attachment.save(file_name)

        else:
            if  link_data[message.content.lower()[1:]]["maker"] == message.author.name :
                with open(file_name, 'w') as fichier:
                    for attachment in message.attachments:
                        await attachment.save(file_name)
            else:
                await message.channel.send("vous n'ête pas le créateur de se server")


client.run("token")
