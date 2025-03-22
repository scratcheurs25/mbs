import discord
import json
import os


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
            
            await message.channel.send(link_data[message.content.lower()[1:]]["version"])
            if link_data[message.content.lower()[1:]]["to_big"] == "false":
                await message.channel.send(file=discord.File(file_path))
            else:
                await message.channel.send(link_data[message.content.lower()[1:]]["file"])
        except Exception as e:
           await message.channel.send(f"Le serveur `{message.content.lower()[1:]}` n'existe pas ou le fichier est introuvable.")
    elif message.content.lower().startswith("€"):
        left_side = message.content.lower()[1:].split("@")[0]
        try:
            right_side = message.content.lower()[1:].split("@")[1]
            file_name = "v_list/" + left_side+".zip"
            if not os.path.exists(file_name):
                with open(file_name, 'w') as fichier:
                    if os.path.exists('link.json'):
                        with open('link.json', 'r') as json_file:
                            link_data = json.load(json_file)
                    else:
                        link_data = {}
                    link_data[left_side] = {
                        "file": left_side + ".zip",
                        "maker": message.author.name,
                        "version": right_side,
                        "to_big" : "false"
                    }
                    with open('link.json', 'w') as json_file:
                        json.dump(link_data, json_file, indent=4)
                        for attachment in message.attachments:
                            await attachment.save(file_name)

            else:
                if  link_data[left_side]["maker"] == message.author.name :
                    with open(file_name, 'w') as fichier:
                        for attachment in message.attachments:
                            await attachment.save(file_name)
                    link_data[left_side]["version"] = right_side
                else:
                    await message.channel.send("vous n'ête pas le créateur de se server")
        except Exception as e:
            await message.channel.send("ajouter une version avec €name@version")
    elif message.content.lower().startswith("&"):
        left_side = message.content.lower()[1:].split("@")[0]
        try:
            right_side = message.content.lower()[1:].split("@")[1]
            last_side = message.content.lower()[1:].split("@")[2]
            if link_data[left_side]["file"]:
                    if os.path.exists('link.json'):
                        with open('link.json', 'r') as json_file:
                            link_data = json.load(json_file)
                    else:
                        link_data = {}
                    link_data[left_side] = {
                        "file": last_side,
                        "maker": message.author.name,
                        "version": right_side,
                        "to_big" : "true"
                    }
                    with open('link.json', 'w') as json_file:
                        json.dump(link_data, json_file, indent=4)

            else:
                if  link_data[left_side]["maker"] == message.author.name :
                    link_data[left_side]["version"] = right_side
                    link_data[left_side]["file"] = last_side
                    link_data[left_side]["to_big"] = "true"
                else:
                    await message.channel.send("vous n'ête pas le créateur de se server")
        except Exception as e:
            await message.channel.send("ajouter une version avec €name@version@liendufichier")
    elif message.content.lower().startswith("/"):
        message_cont = message.content.lower()[1:]
        p1 = message_cont.split('@')[0]
        p2 = message_cont.split('@')[1]
        p3 = message_cont.split('@')[2]
        with open('link.json', 'r') as json_file:
            link_data = json.load(json_file)
        if p1 == "setfileof":
            if link_data[p2]["maker"] == message.author.name and link_data[p2]["to_big"] == "false":
                link_data[p2]["file"] = p3
                with open('link.json', 'w') as json_file:
                    json.dump(link_data, json_file, indent=4)
        if p1 == "seturlof":
            if link_data[p2]["maker"] == message.author.name and link_data[p2]["to_big"] == "true":
                link_data[p2]["file"] = p3
                with open('link.json', 'w') as json_file:
                    json.dump(link_data, json_file, indent=4)
        if p1 == "to_big":
            if link_data[p2]["maker"] == message.author.name:
                link_data[p2]["to_big"] = p3
                with open('link.json', 'w') as json_file:
                    json.dump(link_data, json_file, indent=4)
        if p1 == "makefile":
            file_name = "v_list/" + p2 +"."+p3
            with open(file_name, 'w') as fichier:
                for attachment in message.attachments:
                    await attachment.save(file_name)
        if p1 == "changemaker":
            if link_data[p2]["maker"] == message.author.name:
                link_data[p2]["maker"] = p3
                with open('link.json', 'w') as json_file:
                    json.dump(link_data, json_file, indent=4)
        if p1 == "changevalue":
            p4 = message_cont.split('@')[3]
            if link_data[p2]["maker"] == message.author.name:
                link_data[p2][p3] = p4
                with open('link.json', 'w') as json_file:
                    json.dump(link_data, json_file, indent=4)


client.run("remplace par le token du bot")
