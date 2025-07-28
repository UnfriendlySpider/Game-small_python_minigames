"""
Movement commands for Text Adventure Game.
Handles player movement and room exploration.
"""

from typing import List, Dict, Any
from commands.base_command import BaseCommand, CommandResult
from config.settings import DIRECTIONS, DIRECTION_ALIASES


class GoCommand(BaseCommand):
    """Command for moving in a specific direction."""
    
    def __init__(self):
        super().__init__(
            name="go",
            aliases=["move", "walk", "travel"],
            description="Move in a specified direction",
            help_text="Move in a specified direction. Usage: go <direction> (e.g., 'go north', 'go up')"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the go command."""
        # Validate arguments
        is_valid, error_msg = self.validate_args(args, min_args=1, max_args=1)
        if not is_valid:
            return {"success": False, "message": error_msg}
        
        direction = args[0].lower()
        
        # Normalize direction using aliases
        if direction in DIRECTION_ALIASES:
            direction = DIRECTION_ALIASES[direction]
        
        # Check if it's a valid direction
        if direction not in DIRECTIONS:
            return {
                "success": False, 
                "message": f"'{direction}' is not a valid direction. Valid directions are: {', '.join(DIRECTIONS)}"
            }
        
        # Get current room and player
        current_room = game_state.get("current_room")
        player = game_state.get("player")
        rooms = game_state.get("rooms", {})
        
        if not current_room or not player:
            return {"success": False, "message": "Game state error: missing room or player data."}
        
        # Check if exit exists
        next_room_id = current_room.get_exit(direction)
        if not next_room_id:
            return {"success": False, "message": "You can't go that way."}
        
        # Get destination room
        next_room = rooms.get(next_room_id)
        if not next_room:
            return {"success": False, "message": f"Error: Destination room '{next_room_id}' not found."}
        
        # Check if room can be entered
        can_enter, reason = next_room.can_enter(player.inventory)
        if not can_enter:
            return {"success": False, "message": reason}
        
        # Move player
        player.move_to_room(next_room_id)
        
        # Update game state
        game_state["current_room"] = next_room
        
        # Handle room lighting
        if next_room.dark and not next_room.lit and player.has_light_source:
            next_room.light_room()
        
        # Describe the new room
        next_room.describe(player.has_light_source)
        
        return {
            "success": True,
            "message": "",
            "data": {"new_room": next_room_id, "direction": direction}
        }


class LookCommand(BaseCommand):
    """Command for examining the current room or specific items."""
    
    def __init__(self):
        super().__init__(
            name="look",
            aliases=["l", "observe", "examine room"],
            description="Look around the current room",
            help_text="Look around the current room to see the description and available items/exits."
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the look command."""
        current_room = game_state.get("current_room")
        player = game_state.get("player")
        
        if not current_room or not player:
            return {"success": False, "message": "Game state error: missing room or player data."}
        
        # If no arguments, look at the room
        if not args:
            current_room.describe(player.has_light_source)
            return {"success": True, "message": ""}
        
        # If arguments provided, look at specific item/direction
        target = " ".join(args).lower()
        
        # Check if looking at an exit
        if target in DIRECTIONS or target in DIRECTION_ALIASES:
            direction = DIRECTION_ALIASES.get(target, target)
            next_room_id = current_room.get_exit(direction)
            
            if next_room_id:
                return {
                    "success": True,
                    "message": f"To the {direction}, you see a passage leading to another area."
                }
            else:
                return {
                    "success": True,
                    "message": f"There's nothing to the {direction} but solid wall."
                }
        
        # Check if looking at an item in the room
        item = current_room.find_item(target)
        if item:
            return {
                "success": True,
                "message": item.examine()
            }
        
        # Check if looking at an item in inventory
        inventory_item = player.find_item_in_inventory(target)
        if inventory_item:
            return {
                "success": True,
                "message": inventory_item.examine()
            }
        
        return {
            "success": False,
            "message": f"You don't see '{target}' here."
        }


class ExamineCommand(BaseCommand):
    """Command for examining items in detail."""
    
    def __init__(self):
        super().__init__(
            name="examine",
            aliases=["inspect", "check", "study"],
            description="Examine an item closely",
            help_text="Examine an item closely to get detailed information. Usage: examine <item>"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the examine command."""
        # Validate arguments
        is_valid, error_msg = self.validate_args(args, min_args=1)
        if not is_valid:
            return {"success": False, "message": error_msg}
        
        target = " ".join(args).lower()
        current_room = game_state.get("current_room")
        player = game_state.get("player")
        
        if not current_room or not player:
            return {"success": False, "message": "Game state error: missing room or player data."}
        
        # Check room items first
        item = current_room.find_item(target)
        if item:
            return {
                "success": True,
                "message": item.examine()
            }
        
        # Check inventory items
        inventory_item = player.find_item_in_inventory(target)
        if inventory_item:
            return {
                "success": True,
                "message": inventory_item.examine()
            }
        
        # Special cases for room features
        if target in ["room", "area", "surroundings"]:
            current_room.describe(player.has_light_source)
            return {"success": True, "message": ""}
        
        return {
            "success": False,
            "message": f"You don't see '{target}' here to examine."
        }


# Create directional movement commands
class DirectionalCommand(BaseCommand):
    """Base class for directional movement commands (north, south, etc.)."""
    
    def __init__(self, direction: str):
        aliases = []
        if direction in DIRECTION_ALIASES.values():
            # Find aliases for this direction
            aliases = [alias for alias, full_dir in DIRECTION_ALIASES.items() if full_dir == direction]
        
        super().__init__(
            name=direction,
            aliases=aliases,
            description=f"Move {direction}",
            help_text=f"Move {direction}. Shortcut for 'go {direction}'."
        )
        self.direction = direction
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the directional command by delegating to GoCommand."""
        go_command = GoCommand()
        return go_command.execute([self.direction], game_state)


def create_directional_commands() -> List[BaseCommand]:
    """Create all directional movement commands."""
    commands = []
    
    # Create commands for all directions
    for direction in DIRECTIONS:
        commands.append(DirectionalCommand(direction))
    
    return commands


def get_all_movement_commands() -> List[BaseCommand]:
    """Get all movement-related commands."""
    commands = [
        GoCommand(),
        LookCommand(),
        ExamineCommand()
    ]
    
    # Add directional commands
    commands.extend(create_directional_commands())
    
    return commands
