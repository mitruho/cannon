import json
import os

SAVE_FILE = "game_saves.json"

def load_saves():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as file:
            saves = json.load(file)
            print(f"Loaded Saves from File: {saves}")
            return saves
    else:
        return [None, None, None]

def save_game(slot, player_data):
    saves = load_saves()
    if 0 <= slot < len(saves):
        saves[slot] = player_data
        with open(SAVE_FILE, 'w') as file:
            json.dump(saves, file)
        print(f"Saved Game: {saves}")
        return True
    return False

def load_game(slot):
    saves = load_saves()
    if 0 <= slot < len(saves) and saves[slot] is not None:
        print(f"Loaded Game from Slot {slot}: {saves[slot]}")
        return saves[slot]
    return None

def delete_save(slot):
    saves = load_saves()
    if 0 <= slot < len(saves):
        saves[slot] = None
        with open(SAVE_FILE, 'w') as file:
            json.dump(saves, file)
        return True
    return False

