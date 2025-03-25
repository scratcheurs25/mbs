import json
message = ""
def get_last_user_name():
    with open("py_info.json", 'r') as fichier:
        py_info = json.load(fichier)

def get_last_message():
    with open("py_info.json", 'r') as fichier:
        py_info = json.load(fichier)
    return  py_info["last_message"]
def get_args(num,command):
    return command.split("@")[num]
def get_config():
    with open("py_info.json", 'r') as fichier:
        py_info = json.load(fichier)
    return  py_info["config"]
def setMessage(mess):
    global message
    message = mess