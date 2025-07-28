"""
Inventory commands for Text Adventure Game.
Handles item management and inventory operations.
"""

from typing import List, Dict, Any
from commands.base_command import BaseCommand, CommandResult
from config.game_data import MESSAGES


class GetCommand(BaseCommand):
    """Command for picking up items from the current room."""
    
    def __init__(self):
        super().__init__(
            name="get",
            aliases=["take", "pick up", "grab"],
            description="Pick up an item from the current room",
            help_text="Pick up an item from the current room. Usage: get <item>"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the get command."""
        # Validate arguments
        is_valid, error_msg = self.validate_args(args, min_args=1)
        if not is_valid:
            return {"success": False, "message": error_msg}
        
        item_name = " ".join(args).lower()
        current_room = game_state.get("current_room")
        player = game_state.get("player")
        
        if not current_room or not player:
            return {"success": False, "message": "Game state error: missing room or player data."}
        
        # Check if room is too dark to see items
        if current_room.dark and not (current_room.lit or player.has_light_source):
            return {"success": False, "message": MESSAGES["room_dark"]}
        
        # Find the item in the room
        item = current_room.find_item(item_name)
        if not item:
            return {"success": False, "message": MESSAGES["item_not_found"]}
        
        # Try to add item to player's inventory
        if not player.add_to_inventory(item):
            # Check specific reason for failure
            if len(player.inventory) >= player.max_inventory_size:
                return {"success": False, "message": MESSAGES["inventory_full"]}
            elif player.get_total_weight() + item.get_weight() > player.get_max_carrying_capacity():
                return {
                    "success": False, 
                    "message": f"The {item.name} is too heavy. You're carrying {player.get_total_weight()}/{player.get_max_carrying_capacity()} kg."
                }
            else:
                return {"success": False, "message": "You can't pick up that item right now."}
        
        # Remove item from room
        current_room.remove_item(item)
        
        return {
            "success": True,
            "message": MESSAGES["item_taken"].format(item=item.name),
            "data": {"item_taken": item.item_id}
        }


class DropCommand(BaseCommand):
    """Command for dropping items from inventory."""
    
    def __init__(self):
        super().__init__(
            name="drop",
            aliases=["put down", "leave"],
            description="Drop an item from your inventory",
            help_text="Drop an item from your inventory into the current room. Usage: drop <item>"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the drop command."""
        # Validate arguments
        is_valid, error_msg = self.validate_args(args, min_args=1)
        if not is_valid:
            return {"success": False, "message": error_msg}
        
        item_name = " ".join(args).lower()
        current_room = game_state.get("current_room")
        player = game_state.get("player")
        
        if not current_room or not player:
            return {"success": False, "message": "Game state error: missing room or player data."}
        
        # Find the item in player's inventory
        item = player.find_item_in_inventory(item_name)
        if not item:
            return {"success": False, "message": "You don't have that item."}
        
        # Remove item from player's inventory
        player.remove_from_inventory(item)
        
        # Add item to current room
        current_room.add_item(item)
        
        return {
            "success": True,
            "message": MESSAGES["item_dropped"].format(item=item.name),
            "data": {"item_dropped": item.item_id}
        }


class InventoryCommand(BaseCommand):
    """Command for displaying the player's inventory."""
    
    def __init__(self):
        super().__init__(
            name="inventory",
            aliases=["i", "inv", "items"],
            description="Show your inventory",
            help_text="Display all items you are currently carrying."
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the inventory command."""
        player = game_state.get("player")
        
        if not player:
            return {"success": False, "message": "Game state error: missing player data."}
        
        inventory_display = player.get_inventory_display()
        
        return {
            "success": True,
            "message": inventory_display,
            "data": {"inventory_count": len(player.inventory)}
        }


class UseCommand(BaseCommand):
    """Command for using items from inventory."""
    
    def __init__(self):
        super().__init__(
            name="use",
            aliases=["activate", "employ"],
            description="Use an item from your inventory",
            help_text="Use an item from your inventory. Usage: use <item>"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the use command."""
        # Validate arguments
        is_valid, error_msg = self.validate_args(args, min_args=1)
        if not is_valid:
            return {"success": False, "message": error_msg}
        
        item_name = " ".join(args).lower()
        current_room = game_state.get("current_room")
        player = game_state.get("player")
        
        if not current_room or not player:
            return {"success": False, "message": "Game state error: missing room or player data."}
        
        # Find the item in player's inventory
        item = player.find_item_in_inventory(item_name)
        if not item:
            return {"success": False, "message": "You don't have that item."}
        
        # Create context for item use
        context = {
            "current_room": current_room,
            "player": player,
            "room_id": current_room.room_id
        }
        
        # Use the item
        result = player.use_item(item, context)
        
        # Handle special item effects
        if result["success"]:
            effects = result.get("effects", {})
            
            # Handle room unlocking
            if item.item_id == "key" and current_room.locked and not current_room.unlocked:
                if current_room.unlock_with_item(item):
                    result["message"] += f" You unlock the {current_room.name}!"
            
            # Handle room lighting
            if "provides_light" in effects:
                if current_room.dark and not current_room.lit:
                    current_room.light_room()
                    result["message"] += " The room is now illuminated!"
        
        return {
            "success": result["success"],
            "message": result["message"],
            "data": {
                "item_used": item.item_id,
                "effects": result.get("effects", {}),
                "consumed": result.get("consumed", False)
            }
        }


class StatusCommand(BaseCommand):
    """Command for displaying player status."""
    
    def __init__(self):
        super().__init__(
            name="status",
            aliases=["stat", "health"],
            description="Show your current status",
            help_text="Display your current health, energy, and other status information."
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the status command."""
        player = game_state.get("player")
        
        if not player:
            return {"success": False, "message": "Game state error: missing player data."}
        
        status_display = player.get_status_display()
        
        return {
            "success": True,
            "message": status_display,
            "data": {
                "health": player.health,
                "max_health": player.max_health,
                "energy": player.energy,
                "max_energy": player.max_energy
            }
        }


class StatsCommand(BaseCommand):
    """Command for displaying detailed player statistics."""
    
    def __init__(self):
        super().__init__(
            name="stats",
            aliases=["statistics", "character"],
            description="Show detailed character statistics",
            help_text="Display detailed character statistics including attributes and progress."
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the stats command."""
        player = game_state.get("player")
        
        if not player:
            return {"success": False, "message": "Game state error: missing player data."}
        
        stats_display = player.get_stats_display()
        
        return {
            "success": True,
            "message": stats_display,
            "data": {
                "stats": player.stats.copy(),
                "rooms_visited": len(player.rooms_visited),
                "items_found": len(player.items_found),
                "actions_taken": player.actions_taken,
                "game_time": player.game_time
            }
        }


class EquipCommand(BaseCommand):
    """Command for equipping items."""
    
    def __init__(self):
        super().__init__(
            name="equip",
            aliases=["wield", "wear"],
            description="Equip an item from your inventory",
            help_text="Equip a weapon, armor, or accessory. Usage: equip <item>"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the equip command."""
        # Validate arguments
        is_valid, error_msg = self.validate_args(args, min_args=1)
        if not is_valid:
            return {"success": False, "message": error_msg}
        
        item_name = " ".join(args).lower()
        player = game_state.get("player")
        
        if not player:
            return {"success": False, "message": "Game state error: missing player data."}
        
        # Find the item in player's inventory
        item = player.find_item_in_inventory(item_name)
        if not item:
            return {"success": False, "message": "You don't have that item."}
        
        # Determine equipment slot
        equipment_slot = None
        if item.weapon:
            equipment_slot = "weapon"
        elif hasattr(item, 'armor') and item.armor:
            equipment_slot = "armor"
        elif hasattr(item, 'accessory') and item.accessory:
            equipment_slot = "accessory"
        
        if not equipment_slot:
            return {"success": False, "message": f"The {item.name} cannot be equipped."}
        
        # Unequip current item in that slot if any
        current_equipped = player.equipment.get(equipment_slot)
        if current_equipped:
            message = f"You unequip the {current_equipped.name} and equip the {item.name}."
        else:
            message = f"You equip the {item.name}."
        
        # Equip the item
        player.equipment[equipment_slot] = item
        
        return {
            "success": True,
            "message": message,
            "data": {
                "equipped_item": item.item_id,
                "equipment_slot": equipment_slot,
                "previously_equipped": current_equipped.item_id if current_equipped else None
            }
        }


class UnequipCommand(BaseCommand):
    """Command for unequipping items."""
    
    def __init__(self):
        super().__init__(
            name="unequip",
            aliases=["remove", "unwield"],
            description="Unequip an equipped item",
            help_text="Unequip a currently equipped item. Usage: unequip <item> or unequip <slot>"
        )
    
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the unequip command."""
        # Validate arguments
        is_valid, error_msg = self.validate_args(args, min_args=1)
        if not is_valid:
            return {"success": False, "message": error_msg}
        
        target = " ".join(args).lower()
        player = game_state.get("player")
        
        if not player:
            return {"success": False, "message": "Game state error: missing player data."}
        
        # Check if target is an equipment slot
        if target in player.equipment:
            equipped_item = player.equipment[target]
            if not equipped_item:
                return {"success": False, "message": f"You don't have anything equipped in the {target} slot."}
            
            player.equipment[target] = None
            return {
                "success": True,
                "message": f"You unequip the {equipped_item.name}.",
                "data": {"unequipped_item": equipped_item.item_id, "equipment_slot": target}
            }
        
        # Check if target is an equipped item
        for slot, equipped_item in player.equipment.items():
            if equipped_item and equipped_item.matches_keyword(target):
                player.equipment[slot] = None
                return {
                    "success": True,
                    "message": f"You unequip the {equipped_item.name}.",
                    "data": {"unequipped_item": equipped_item.item_id, "equipment_slot": slot}
                }
        
        return {"success": False, "message": f"You don't have '{target}' equipped."}


def get_all_inventory_commands() -> List[BaseCommand]:
    """Get all inventory-related commands."""
    return [
        GetCommand(),
        DropCommand(),
        InventoryCommand(),
        UseCommand(),
        StatusCommand(),
        StatsCommand(),
        EquipCommand(),
        UnequipCommand()
    ]
