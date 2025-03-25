import os
import discord
import json
import re
import subprocess
import logging

# Lire le fichier JSON
with open('link.json', 'r') as json_file:
    link_data = json.load(json_file)
with open('py_info.json', 'r') as json_file:
    py_info = json.load(json_file)

logging.basicConfig(
    filename="bot_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)




intents = discord.Intents.default()
intents.messages = True
intents.message_content  = True
intents.members = True

client = discord.Client(intents=intents)

def S_exec(script):
    # Validez le contenu de script ici avant exécution.
    try:
        logging.info(f"Exécution du script: {script}")
        result = subprocess.run(["python3", "-c", script], capture_output=True, text=True)
        logging.info(f"code executer {script}, donne,{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Erreur dans l'exécution : {e}"

def makeFilePath(filename):
    filename = os.path.basename(filename)
    filename = os.path.join("v_list", filename)
    return filename



def python_filter(script, allowed_libs=["py_mmb_libs"]):
    # Regex pour capturer les imports
    import_statements = re.findall(r"^\s*(?:from\s+(\w+)\s+import\s+\w+|import\s+(\w+))", script, re.MULTILINE)
    imported_modules = {mod for imp in import_statements for mod in imp if mod}
    if not imported_modules.issubset(set(allowed_libs)):
        logging.info(f"import blocker dans {script}")
        return False  # Un import non autorisé a été détecté
    forbidden_keywords = ["exec(", "eval(", "open(", "subprocess", "os.", "sys.", "shutil.", "__import__", "compile(", "globals(", "locals("]
    if any(keyword in script for keyword in forbidden_keywords):
        logging.info(f"code interdit dans {script}")
        return False


    return True

def ds(script):
    logging.info(f"{script} executer dans ds")
    if script.startswith("says "):
        script = script[5:]
        return script
    if script.startswith("ip "):
        script = " l'ip du server est " + script[3:]
        return script
    if script.startswith("open"):
        with open(makeFilePath(script[5:]),'r') as file:
            script = file.read()
        return script
    if script.startswith("py "):
        if not script[3:] == "help":
            with open(makeFilePath(script[3:]+ ".py"),'r') as file:
                script = file.read()
        else:
            with open("help.py",'r') as file:
                script = file.read()
        if python_filter(script):
            script = S_exec(script)
            return script
    return ""

@client.event
async def on_ready():
    print("ready")

@client.event
async def on_message(message):
    global link_data,py_info
    if message.author == client.user:
        return
    logging.info(f"{message.content} evoyer dans discord par {message.author.name}")
    with open("py_info.json", 'r') as fichier:
        py_info = json.load(fichier)
    try:
        py_info = {
        "last_message": message.content,
        "last_user": message.author.name,
        "config": link_data[message.content.lower()[1:]]["config"]
        }
    except:
        py_info = {
            "last_message": message.content,
            "last_user": message.author.name,
            "config": ""
        }
        print("message non valide")
    with open('py_info.json', 'w') as json_file:
        json.dump(py_info, json_file, indent=4)


    if message.content.lower().startswith("!"):
        logging.info(f"{message.author.name} a accerder au mod-pack {message.content.lower()[1:]}")
        try:
            name = message.content.lower()[1:].split("@")[0]
            # Construit le chemin vers le fichier
            file_path = makeFilePath(link_data[name]["file"])

            try:
                if link_data[name]["cs"] == "true":
                    script = link_data[name]["cc"]
                    script = ds(script)
                    await message.channel.send(script)
            except Exception as r:
                print(r)

            if not link_data[name]["is_command"] == "true":
                await message.channel.send(link_data[name]["version"])
                if link_data[name]["to_big"] == "false":
                    await message.channel.send(file=discord.File(file_path))
                else:
                    await message.channel.send(link_data[name]["file"])
        except Exception as e:
           await message.channel.send(f"Le serveur `{message.content.lower()[1:]}` n'existe pas ou le fichier est introuvable.")
           logging.info(f"{message.author.name} a assayer d'acceder au mod-pack {message.content.lower()[1:]} mais il existe pas ou le fichier est introuvable,{e} ")
    elif message.content.lower().startswith("-"):
        logging.info(f"{message.author.name} a créer ou modifier le mod-pack {message.content.lower()[1:]}")
        left_side = message.content.lower()[1:].split("@")[0]
        logging.info(f"le nom du mod pack est {left_side}")
        try:
            right_side = message.content.lower()[1:].split("@")[1]
            file_name = makeFilePath(left_side+".zip")
            if not os.path.exists(file_name):
                logging.info(f"{message.author.name} a créer le mod-pack {message.content.lower()[1:]}")
                with open(file_name, 'w') as fichier:
                    with open('link.json', 'r') as json_file:
                        link_data = json.load(json_file)
                    logging.info(f"link.json ouvert")
                    link_data[left_side] = {
                        "file": left_side + ".zip",
                        "maker": message.author.name,
                        "version": right_side,
                        "to_big" : "false",
                        "is_command": "false",
                        "config":""
                    }
                    logging.info(f"link.json modifier")
                    with open('link.json', 'w') as json_file:
                        json.dump(link_data, json_file, indent=4)
                        for attachment in message.attachments:
                            await attachment.save(file_name)
                    logging.info(f"link.json sauvegarder")

            else:
                if  link_data[left_side]["maker"] == message.author.name :
                    logging.info(f"mod-pack {left_side} modifier")
                    with open(file_name, 'w') as fichier:
                        for attachment in message.attachments:
                            await attachment.save(file_name)
                    logging.info(f"fichier de mod-pack {left_side} modifier")
                    link_data[left_side] = {
                        "file": left_side + ".zip",
                        "maker": message.author.name,
                        "version": right_side,
                        "to_big": "false",
                        "is_command": "false",
                    }
                    logging.info(f"link.json modifier")
                    with open('link.json', 'w') as json_file:
                        json.dump(link_data, json_file, indent=4)
                else:
                    await message.channel.send("vous n'ête pas le créateur de se server")
        except Exception as e:
            await message.channel.send(f"ajouter une version avec €name@version,{e}")
    elif message.content.lower().startswith("*"):
        logging.info(f"{message.author.name} a créer ou modifier le mod-pack {message.content.lower()[1:]}")
        left_side = message.content.lower()[1:].split("@")[0]
        logging.info(f"le mod-pack est{left_side}")
        try:
            right_side = message.content.lower()[1:].split("@")[1]
            last_side = message.content.lower()[1:].split("@")[2]
            file_name = makeFilePath(left_side + ".zip")
            if not os.path.exists(file_name):
                    with open('link.json', 'r') as json_file:
                            link_data = json.load(json_file)
                    link_data[left_side] = {
                        "file": last_side,
                        "maker": message.author.name,
                        "version": right_side,
                        "to_big" : "true",
                        "is_command": "false",
                        "config":""
                    }
                    with open('link.json', 'w') as json_file:
                        json.dump(link_data, json_file, indent=4)
                    with open(file_name, 'w') as fichier:
                        fichier.write('')
                    logging.info("mod-pack créer")
            else:
                if  link_data[left_side]["maker"] == message.author.name :
                    link_data[left_side]["version"] = right_side
                    link_data[left_side]["file"] = last_side
                    link_data[left_side]["to_big"] = "true"
                    with open('link.json', 'w') as json_file:
                        json.dump(link_data, json_file, indent=4)
                    logging.info("mod-pack modifier")
                else:
                    await message.channel.send("vous n'ête pas le créateur de se server")
        except Exception as e:
            await message.channel.send(f"ajouter une version avec €name@version@liendufichier")
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
            file_name = makeFilePath(p2 +"."+p3)
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
        if p1 == "makescript":
            if link_data[p2]["maker"] == message.author.name:
                link_data[p2]["cs"] = "true"
                link_data[p2]["cc"] = p3
                with open('link.json', 'w') as json_file:
                    json.dump(link_data, json_file, indent=4)
        if p1 == "is_command":
            if link_data[p2]["maker"] == message.author.name:
                link_data[p2]["is_command"] = p3
                with open('link.json', 'w') as json_file:
                    json.dump(link_data, json_file, indent=4)
if __name__ == "__main__":
    client.run(os.getenv("DISCORD_TOKEN"))
