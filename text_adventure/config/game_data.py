"""
Game data definitions for Text Adventure Game.
Contains room definitions, items, and game content.
"""

from typing import Dict, List, Any, Optional


# Item definitions
ITEMS: Dict[str, Dict[str, Any]] = {
    "key": {
        "name": "rusty key",
        "description": "An old, rusty key that looks like it might open something important.",
        "weight": 1,
        "value": 10,
        "usable": True,
        "consumable": False,
        "keywords": ["key", "rusty", "old"]
    },
    "lamp": {
        "name": "oil lamp",
        "description": "A brass oil lamp that provides light in dark places.",
        "weight": 2,
        "value": 25,
        "usable": True,
        "consumable": False,
        "keywords": ["lamp", "oil", "brass", "light"]
    },
    "book": {
        "name": "ancient tome",
        "description": "A leather-bound book filled with mysterious symbols and arcane knowledge.",
        "weight": 3,
        "value": 50,
        "usable": True,
        "consumable": False,
        "keywords": ["book", "tome", "ancient", "leather"]
    },
    "potion": {
        "name": "health potion",
        "description": "A small vial containing a red liquid that glows faintly.",
        "weight": 1,
        "value": 30,
        "usable": True,
        "consumable": True,
        "effect": {"health": 25},
        "keywords": ["potion", "vial", "health", "red"]
    },
    "sword": {
        "name": "iron sword",
        "description": "A well-balanced iron sword with a sharp edge.",
        "weight": 5,
        "value": 100,
        "usable": True,
        "consumable": False,
        "weapon": True,
        "damage": 15,
        "keywords": ["sword", "iron", "weapon", "blade"]
    }
}

# Room definitions
ROOMS: Dict[str, Dict[str, Any]] = {
    "start_room": {
        "name": "Starting Chamber",
        "description": "You find yourself in a dimly lit stone chamber. Ancient torches flicker on the walls, casting dancing shadows. The air is musty and filled with the scent of ages past.",
        "long_description": "This appears to be some kind of ancient chamber, carved from solid stone. The walls are adorned with faded murals depicting scenes of adventure and mystery. A few old torches provide flickering light, and you can hear the distant sound of dripping water echoing through unseen passages.",
        "exits": {
            "north": "kitchen",
            "east": "library"
        },
        "items": ["lamp"],
        "visited": False,
        "dark": False,
        "locked": False
    },
    "kitchen": {
        "name": "Ancient Kitchen",
        "description": "You are in what appears to be an old kitchen. Cobwebs hang from the ceiling, and dust covers every surface. A large stone hearth dominates one wall.",
        "long_description": "This kitchen hasn't been used in decades, perhaps centuries. Rusty pots and pans hang from hooks on the walls, and a massive stone hearth takes up most of the north wall. A wooden table in the center is covered with a thick layer of dust. Despite the abandonment, there's something oddly welcoming about this place.",
        "exits": {
            "south": "start_room",
            "west": "pantry"
        },
        "items": ["key", "potion"],
        "visited": False,
        "dark": False,
        "locked": False
    },
    "library": {
        "name": "Forgotten Library",
        "description": "Towering bookshelves stretch from floor to ceiling, filled with ancient tomes and scrolls. Dust motes dance in shafts of light filtering through high windows.",
        "long_description": "This magnificent library must have once been the pride of whoever built this place. Countless books line the shelves, their leather bindings cracked with age. A reading desk sits in the center, with an ornate chair that looks surprisingly comfortable. The smell of old parchment and leather fills the air.",
        "exits": {
            "west": "start_room",
            "north": "study"
        },
        "items": ["book"],
        "visited": False,
        "dark": False,
        "locked": False
    },
    "pantry": {
        "name": "Storage Pantry",
        "description": "A small storage room with empty shelves lining the walls. It's clear this room once held food and supplies.",
        "long_description": "This cramped pantry shows signs of having once been well-stocked with provisions. Empty barrels and sacks lie scattered about, and the shelves that line the walls are bare except for a few forgotten items. The air is stale and carries a faint scent of old grain.",
        "exits": {
            "east": "kitchen"
        },
        "items": [],
        "visited": False,
        "dark": True,
        "locked": False,
        "requires_light": True
    },
    "study": {
        "name": "Scholar's Study",
        "description": "A cozy study with a large desk covered in papers and writing implements. Bookshelves line the walls, and a comfortable chair sits behind the desk.",
        "long_description": "This intimate study belongs to someone who clearly valued learning and knowledge. The desk is covered with half-finished manuscripts, quill pens, and bottles of dried ink. Personal touches like a small plant (now withered) and a framed portrait suggest this was someone's private sanctuary.",
        "exits": {
            "south": "library"
        },
        "items": ["sword"],
        "visited": False,
        "dark": False,
        "locked": True,
        "unlock_item": "key"
    }
}

# Game messages and text
MESSAGES: Dict[str, str] = {
    "welcome": f"""
{ROOMS['start_room']['long_description']}

Welcome to the Text Adventure Game!
Type 'help' for a list of available commands.
Type 'look' to examine your surroundings more closely.
""",
    "help": """
Available Commands:
  Movement: go <direction>, north, south, east, west, up, down
  Shortcuts: n, s, e, w, ne, nw, se, sw, u, d
  
  Actions: look, examine <item>, get <item>, drop <item>
  Inventory: inventory (or i), use <item>
  
  Game: save [slot], load [slot], quit (or q), help (or h)
  
  You can also use shortcuts like 'n' for 'go north' and 'i' for 'inventory'.
""",
    "quit": "Thanks for playing! Your adventure ends here... for now.",
    "invalid_command": "I don't understand that command. Type 'help' for available commands.",
    "invalid_direction": "You can't go that way.",
    "room_locked": "This room is locked. You need to find a way to open it.",
    "room_dark": "It's too dark to see anything. You need a source of light.",
    "item_not_found": "I don't see that item here.",
    "item_taken": "You take the {item}.",
    "item_dropped": "You drop the {item}.",
    "inventory_full": "Your inventory is full. You need to drop something first.",
    "inventory_empty": "Your inventory is empty.",
    "item_used": "You use the {item}.",
    "cannot_use_item": "You can't use that item here.",
    "already_visited": "You've been here before.",
    "first_visit": "This is your first time in this location."
}

# Command aliases and variations
COMMAND_ALIASES: Dict[str, List[str]] = {
    "look": ["look", "l", "examine room", "observe"],
    "inventory": ["inventory", "i", "inv", "items"],
    "get": ["get", "take", "pick up", "grab"],
    "drop": ["drop", "put down", "leave"],
    "use": ["use", "activate", "employ"],
    "examine": ["examine", "inspect", "check", "study"],
    "help": ["help", "h", "?", "commands"],
    "quit": ["quit", "q", "exit", "bye"],
    "save": ["save", "save game"],
    "load": ["load", "load game"]
}

# Special room behaviors
ROOM_BEHAVIORS: Dict[str, Dict[str, Any]] = {
    "pantry": {
        "on_enter_dark": "You stumble around in the darkness, unable to see anything clearly.",
        "on_enter_lit": "The lamp illuminates dusty shelves and forgotten supplies."
    },
    "study": {
        "on_unlock": "The key turns with a satisfying click, and the door swings open.",
        "unlock_description": "You use the rusty key to unlock the study door."
    }
}


def get_room_data(room_id: str) -> Optional[Dict[str, Any]]:
    """Get room data by ID."""
    return ROOMS.get(room_id)


def get_item_data(item_id: str) -> Optional[Dict[str, Any]]:
    """Get item data by ID."""
    return ITEMS.get(item_id)


def get_all_room_ids() -> List[str]:
    """Get all room IDs."""
    return list(ROOMS.keys())


def get_all_item_ids() -> List[str]:
    """Get all item IDs."""
    return list(ITEMS.keys())


def validate_game_data():
    """Validate game data for consistency."""
    # Check that all room exits point to valid rooms
    for room_id, room_data in ROOMS.items():
        for direction, target_room in room_data.get("exits", {}).items():
            if target_room not in ROOMS:
                raise ValueError(f"Room '{room_id}' has exit to non-existent room '{target_room}'")
    
    # Check that all room items exist in ITEMS
    for room_id, room_data in ROOMS.items():
        for item_id in room_data.get("items", []):
            if item_id not in ITEMS:
                raise ValueError(f"Room '{room_id}' contains non-existent item '{item_id}'")
    
    # Check that unlock items exist
    for room_id, room_data in ROOMS.items():
        unlock_item = room_data.get("unlock_item")
        if unlock_item and unlock_item not in ITEMS:
            raise ValueError(f"Room '{room_id}' requires non-existent unlock item '{unlock_item}'")


# Validate game data on import
validate_game_data()
