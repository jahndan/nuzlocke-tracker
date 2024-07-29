from pynput import keyboard
import json


def on_PartyToDead():
    print("Mark dead")


def on_ToParty():
    print("Send to party")


def on_ToBoxed():
    print("Send to box")


def on_FailEnc():
    print("Fail the encounter")


def on_EditEnc():
    print("Edit an encounter")


config = json.load(open("config.json")).get("keybinds")
hotkeys = dict()
hotkeys[config.get("Mark dead")] = on_PartyToDead
hotkeys[config.get("Send to party")] = on_ToParty
hotkeys[config.get("Send to box")] = on_ToBoxed
hotkeys[config.get("Fail the encounter")] = on_FailEnc
hotkeys[config.get("Edit an encounter")] = on_EditEnc


globalHotkeys = keyboard.GlobalHotKeys(hotkeys)
globalHotkeys.start()
