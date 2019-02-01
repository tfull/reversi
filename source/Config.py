import yaml

DATA = None

def load():
    global DATA
    with open("config.yml", "r") as f:
        DATA = yaml.load(f)

def get(name):
    global DATA
    if DATA is None:
        load()
    return DATA[name]

def get_global(name):
    return get("global")[name]

def get_player(name):
    return get("players")[name]

def get_process(name):
    return get("processes")[name]
