from pynput import keyboard
from common import bold, reset, dbg
from collections import deque
import json


event_queue = deque()
"""pop from left to dequeue in order (events are appended from right)"""


def on_ToParty():
    dbg("HOTKEY", "Send to party")
    event_queue.append("ToParty")


def on_ToBoxed():
    dbg("HOTKEY", "Send to box")
    event_queue.append("ToBoxed")


def on_PartyToDead():
    dbg("HOTKEY", "Mark dead")
    event_queue.append("ToDead")


def on_FailEnc():
    dbg("HOTKEY", "Fail the encounter")
    event_queue.append("FailEnc")


def on_EditEnc():
    dbg("HOTKEY", "Edit an encounter")
    event_queue.append("EditEnc")


try:
    config = json.load(open("config.json")).get("keybinds")
except:
    config = json.load(open("config.defaults.json")).get("keybinds")
finally:
    print(f"{bold}Configured hotkeys{reset}")
    for action, keybind in config.items():
        print(f"  {action}: {bold}{keybind}{reset}")

hotkeys = dict()
hotkeys[config.get("Send to party")] = on_ToParty
hotkeys[config.get("Send to box")] = on_ToBoxed
hotkeys[config.get("Mark dead")] = on_PartyToDead
hotkeys[config.get("Fail the encounter")] = on_FailEnc
hotkeys[config.get("Edit an encounter")] = on_EditEnc

globalHotkeys = keyboard.GlobalHotKeys(hotkeys)
globalHotkeys.start()
