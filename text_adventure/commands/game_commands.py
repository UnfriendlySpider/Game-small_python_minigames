"""
Game management commands for Text Adventure Game.
Handles save/load, help, and game control operations.
"""

import os
import json
from typing import List, Dict, Any
from commands.base_command import BaseCommand, CommandResult
from config.settings import FILES, GAME
from config.game_data import MESSAGES


class HelpCommand(BaseCommand):
    """Command for displaying help information."""
    
    def __init__(self):
        super().__init__(
            name="help",
            aliases=["h", "?", "commands"],
            description="Show available commands and help",
            help_text="Display help information about available commands. Usage: help [command]"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the help command."""
        command_manager = game_state.get("command_manager")
        
        if not command_manager:
            return {"success": False, "message": "Game state error: missing command manager."}
        
        # If no arguments, show general help
        if not args:
            help_text = command_manager.get_help_text()
            help_text += "\n\nType 'help <command>' for detailed information about a specific command."
            return {"success": True, "message": help_text}
        
        # Show help for specific command
        command_name = args[0].lower()
        command = command_manager.get_command(command_name)
        
        if not command:
            return {"success": False, "message": f"Unknown command: {command_name}"}
        
        return {"success": True, "message": command.get_help()}


class QuitCommand(BaseCommand):
    """Command for quitting the game."""
    
    def __init__(self):
        super().__init__(
            name="quit",
            aliases=["q", "exit", "bye"],
            description="Quit the game",
            help_text="Exit the game. You will be prompted to save your progress."
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the quit command."""
        return {
            "success": True,
            "message": MESSAGES["quit"],
            "state_change": "quit"
        }


class SaveCommand(BaseCommand):
    """Command for saving the game."""
    
    def __init__(self):
        super().__init__(
            name="save",
            aliases=["save game"],
            description="Save your game progress",
            help_text="Save your current game progress. Usage: save [slot_number] (1-5)"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the save command."""
        # Determine save slot
        slot = 1  # Default slot
        if args:
            try:
                slot = int(args[0])
                if slot < 1 or slot > GAME.MAX_SAVE_SLOTS:
                    return {
                        "success": False, 
                        "message": f"Invalid save slot. Please use a number between 1 and {GAME.MAX_SAVE_SLOTS}."
                    }
            except ValueError:
                return {"success": False, "message": "Invalid save slot number."}
        
        # Create save directory if it doesn't exist
        save_dir = FILES.SAVE_DIR
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except OSError as e:
                return {"success": False, "message": f"Could not create save directory: {e}"}
        
        # Prepare save data
        player = game_state.get("player")
        rooms = game_state.get("rooms", {})
        current_room = game_state.get("current_room")
        
        if not player or not current_room:
            return {"success": False, "message": "Game state error: missing player or room data."}
        
        save_data = {
            "version": GAME.VERSION,
            "player": player.to_dict(),
            "current_room_id": current_room.room_id,
            "rooms": {room_id: room.to_dict() for room_id, room in rooms.items()},
            "game_time": player.game_time,
            "save_slot": slot,
            "timestamp": __import__('time').time()
        }
        
        # Save to file
        save_filename = f"save_slot_{slot}{FILES.SAVE_EXTENSION}"
        save_path = os.path.join(save_dir, save_filename)
        
        try:
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return {
                "success": True,
                "message": f"Game saved to slot {slot}.",
                "data": {"save_slot": slot, "save_path": save_path}
            }
            
        except Exception as e:
            return {"success": False, "message": f"Failed to save game: {e}"}


class LoadCommand(BaseCommand):
    """Command for loading a saved game."""
    
    def __init__(self):
        super().__init__(
            name="load",
            aliases=["load game"],
            description="Load a saved game",
            help_text="Load a previously saved game. Usage: load [slot_number] (1-5)"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the load command."""
        # Determine save slot
        slot = 1  # Default slot
        if args:
            try:
                slot = int(args[0])
                if slot < 1 or slot > GAME.MAX_SAVE_SLOTS:
                    return {
                        "success": False, 
                        "message": f"Invalid save slot. Please use a number between 1 and {GAME.MAX_SAVE_SLOTS}."
                    }
            except ValueError:
                return {"success": False, "message": "Invalid save slot number."}
        
        # Check if save file exists
        save_filename = f"save_slot_{slot}{FILES.SAVE_EXTENSION}"
        save_path = os.path.join(FILES.SAVE_DIR, save_filename)
        
        if not os.path.exists(save_path):
            return {"success": False, "message": f"No saved game found in slot {slot}."}
        
        # Load save data
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            # Validate save data
            if not self._validate_save_data(save_data):
                return {"success": False, "message": "Save file is corrupted or incompatible."}
            
            return {
                "success": True,
                "message": f"Game loaded from slot {slot}.",
                "data": {
                    "save_data": save_data,
                    "save_slot": slot,
                    "load_requested": True
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Failed to load game: {e}"}
    
    def _validate_save_data(self, save_data: Dict[str, Any]) -> bool:
        """Validate that save data contains required fields."""
        required_fields = ["player", "current_room_id", "rooms"]
        return all(field in save_data for field in required_fields)


class ListSavesCommand(BaseCommand):
    """Command for listing available save files."""
    
    def __init__(self):
        super().__init__(
            name="saves",
            aliases=["list saves", "save list"],
            description="List available save files",
            help_text="Display information about all available save files."
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the list saves command."""
        save_dir = FILES.SAVE_DIR
        
        if not os.path.exists(save_dir):
            return {"success": True, "message": "No save files found."}
        
        save_info = []
        
        for slot in range(1, GAME.MAX_SAVE_SLOTS + 1):
            save_filename = f"save_slot_{slot}{FILES.SAVE_EXTENSION}"
            save_path = os.path.join(save_dir, save_filename)
            
            if os.path.exists(save_path):
                try:
                    with open(save_path, 'r') as f:
                        save_data = json.load(f)
                    
                    # Extract save information
                    player_name = save_data.get("player", {}).get("name", "Unknown")
                    game_time = save_data.get("game_time", 0)
                    timestamp = save_data.get("timestamp", 0)
                    
                    # Format timestamp
                    import time
                    date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                    
                    save_info.append(f"  Slot {slot}: {player_name} - {game_time} minutes - {date_str}")
                    
                except Exception:
                    save_info.append(f"  Slot {slot}: [Corrupted save file]")
            else:
                save_info.append(f"  Slot {slot}: [Empty]")
        
        if save_info:
            message = "Available save files:\n" + "\n".join(save_info)
        else:
            message = "No save files found."
        
        return {"success": True, "message": message}


class NewGameCommand(BaseCommand):
    """Command for starting a new game."""
    
    def __init__(self):
        super().__init__(
            name="new",
            aliases=["new game", "restart"],
            description="Start a new game",
            help_text="Start a new game, discarding current progress."
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the new game command."""
        return {
            "success": True,
            "message": "Starting a new game...",
            "data": {"new_game_requested": True}
        }


class VersionCommand(BaseCommand):
    """Command for displaying game version information."""
    
    def __init__(self):
        super().__init__(
            name="version",
            aliases=["ver", "about"],
            description="Show game version information",
            help_text="Display version and author information about the game."
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the version command."""
        version_info = f"""
{GAME.GAME_TITLE} v{GAME.VERSION}
By {GAME.AUTHOR}

A text-based adventure game with enhanced features including:
- Rich item and inventory system
- Character stats and progression
- Save/load functionality
- Extensible command system
- Dynamic room lighting and unlocking
"""
        
        return {"success": True, "message": version_info.strip()}


class HistoryCommand(BaseCommand):
    """Command for displaying command history."""
    
    def __init__(self):
        super().__init__(
            name="history",
            aliases=["hist", "commands history"],
            description="Show recent command history",
            help_text="Display your recent command history. Usage: history [number]"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the history command."""
        command_manager = game_state.get("command_manager")
        
        if not command_manager:
            return {"success": False, "message": "Game state error: missing command manager."}
        
        # Determine how many commands to show
        limit = 10  # Default
        if args:
            try:
                limit = int(args[0])
                if limit < 1:
                    limit = 10
                elif limit > 50:
                    limit = 50
            except ValueError:
                return {"success": False, "message": "Invalid number for history limit."}
        
        history = command_manager.get_history(limit)
        
        if not history:
            return {"success": True, "message": "No command history available."}
        
        # Format history
        history_lines = ["Recent commands:"]
        for i, command in enumerate(reversed(history), 1):
            history_lines.append(f"  {i:2d}. {command}")
        
        return {"success": True, "message": "\n".join(history_lines)}


def get_all_game_commands() -> List[BaseCommand]:
    """Get all game management commands."""
    return [
        HelpCommand(),
        QuitCommand(),
        SaveCommand(),
        LoadCommand(),
        ListSavesCommand(),
        NewGameCommand(),
        VersionCommand(),
        HistoryCommand()
    ]
