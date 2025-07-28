"""
Enhanced Player system for Text Adventure Game.
Represents the player character with stats, inventory, and abilities.
"""

from typing import Dict, List, Any, Optional
from config.settings import PLAYER
from entities.item import Item, find_item_by_keyword


class Player:
    """
    Represents the player character in the text adventure game.
    
    Attributes:
        name (str): The player's name
        current_room (str): ID of the room the player is currently in
        inventory (List[Item]): Items the player is carrying
        health (int): Current health points
        max_health (int): Maximum health points
        energy (int): Current energy points
        max_energy (int): Maximum energy points
        stats (Dict[str, int]): Player statistics
        effects (Dict[str, Any]): Active effects on the player
    """
    
    def __init__(self, name: str, starting_room: str):
        """
        Initialize a new Player instance.
        
        Args:
            name: The player's name
            starting_room: ID of the starting room
        """
        self.name = name
        self.current_room = starting_room
        
        # Inventory system
        self.inventory: List[Item] = []
        self.max_inventory_size = PLAYER.MAX_INVENTORY_SIZE
        
        # Health and energy
        self.health = PLAYER.STARTING_HEALTH
        self.max_health = PLAYER.STARTING_HEALTH
        self.energy = PLAYER.STARTING_ENERGY
        self.max_energy = PLAYER.STARTING_ENERGY
        
        # Player statistics
        self.stats = {
            "strength": 10,
            "dexterity": 10,
            "intelligence": 10,
            "luck": 10,
            "experience": 0,
            "level": 1
        }
        
        # Active effects (buffs/debuffs)
        self.effects: Dict[str, Dict[str, Any]] = {}
        
        # Equipment slots
        self.equipment = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }
        
        # Game progress tracking
        self.rooms_visited: set = {starting_room}
        self.items_found: set = set()
        self.actions_taken = 0
        self.game_time = 0  # in game minutes
        
        # Player state
        self.is_alive = True
        self.has_light_source = False
        self.carrying_capacity = 0
    
    def __str__(self) -> str:
        """Return string representation of the player."""
        return self.name
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return f"Player(name='{self.name}', room='{self.current_room}', health={self.health})"
    
    def move_to_room(self, room_id: str) -> None:
        """
        Move the player to a new room.
        
        Args:
            room_id: ID of the destination room
        """
        self.current_room = room_id
        self.rooms_visited.add(room_id)
        self.actions_taken += 1
        self.game_time += 1  # Each move takes 1 game minute
    
    def add_to_inventory(self, item: Item) -> bool:
        """
        Add an item to the player's inventory.
        
        Args:
            item: Item to add
            
        Returns:
            bool: True if item was added successfully
        """
        # Check inventory space
        if len(self.inventory) >= self.max_inventory_size:
            return False
        
        # Check carrying capacity
        if self.get_total_weight() + item.get_weight() > self.get_max_carrying_capacity():
            return False
        
        # Try to combine with existing items
        for existing_item in self.inventory:
            if existing_item.item_id == item.item_id:
                if existing_item.combine_with(item):
                    self.items_found.add(item.item_id)
                    return True
        
        # Add as new item
        self.inventory.append(item)
        self.items_found.add(item.item_id)
        self.actions_taken += 1
        return True
    
    def remove_from_inventory(self, item: Item) -> bool:
        """
        Remove an item from the player's inventory.
        
        Args:
            item: Item to remove
            
        Returns:
            bool: True if item was removed
        """
        if item in self.inventory:
            self.inventory.remove(item)
            self.actions_taken += 1
            return True
        return False
    
    def find_item_in_inventory(self, keyword: str) -> Optional[Item]:
        """
        Find an item in inventory by keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            Item if found, None otherwise
        """
        return find_item_by_keyword(self.inventory, keyword)
    
    def has_item(self, item_id: str) -> bool:
        """
        Check if player has a specific item.
        
        Args:
            item_id: ID of the item to check for
            
        Returns:
            bool: True if player has the item
        """
        return any(item.item_id == item_id for item in self.inventory)
    
    def get_item_count(self, item_id: str) -> int:
        """
        Get the total quantity of a specific item.
        
        Args:
            item_id: ID of the item to count
            
        Returns:
            int: Total quantity of the item
        """
        total = 0
        for item in self.inventory:
            if item.item_id == item_id:
                total += item.quantity
        return total
    
    def use_item(self, item: Item, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Use an item from inventory.
        
        Args:
            item: Item to use
            context: Optional context for item use
            
        Returns:
            Dict containing the result of using the item
        """
        if item not in self.inventory:
            return {
                "success": False,
                "message": "You don't have that item.",
                "consumed": False
            }
        
        result = item.use(context)
        
        if result["success"]:
            # Apply effects to player
            effects = result.get("effects", {})
            
            # Handle health effects
            if "health" in effects:
                self.heal(effects["health"])
                result["message"] += f" You gain {effects['health']} health."
            
            # Handle light source
            if "provides_light" in effects:
                self.has_light_source = True
            
            # Handle weapon equipping
            if "weapon_equipped" in effects:
                self.equipment["weapon"] = item
            
            # Remove item if consumed
            if result["consumed"]:
                if item.quantity > 1:
                    item.quantity -= 1
                else:
                    self.remove_from_inventory(item)
        
        return result
    
    def get_inventory_display(self) -> str:
        """
        Get a formatted display of the inventory.
        
        Returns:
            str: Formatted inventory display
        """
        if not self.inventory:
            return "Your inventory is empty."
        
        lines = ["Your inventory contains:"]
        for i, item in enumerate(self.inventory, 1):
            weight_info = f" ({item.get_weight()} kg)" if item.get_weight() > 1 else ""
            lines.append(f"  {i}. {item}{weight_info}")
        
        # Add carrying capacity info
        current_weight = self.get_total_weight()
        max_weight = self.get_max_carrying_capacity()
        lines.append(f"\nCarrying: {current_weight}/{max_weight} kg")
        lines.append(f"Inventory slots: {len(self.inventory)}/{self.max_inventory_size}")
        
        return "\n".join(lines)
    
    def get_total_weight(self) -> int:
        """
        Get the total weight of all items in inventory.
        
        Returns:
            int: Total weight in kg
        """
        return sum(item.get_weight() for item in self.inventory)
    
    def get_max_carrying_capacity(self) -> int:
        """
        Get the maximum carrying capacity based on strength.
        
        Returns:
            int: Maximum carrying capacity in kg
        """
        base_capacity = 20
        strength_bonus = self.stats["strength"] * 2
        return base_capacity + strength_bonus
    
    def heal(self, amount: int) -> int:
        """
        Heal the player by a certain amount.
        
        Args:
            amount: Amount of health to restore
            
        Returns:
            int: Actual amount healed
        """
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health
    
    def take_damage(self, amount: int) -> int:
        """
        Deal damage to the player.
        
        Args:
            amount: Amount of damage to deal
            
        Returns:
            int: Actual damage taken
        """
        old_health = self.health
        self.health = max(0, self.health - amount)
        
        if self.health <= 0:
            self.is_alive = False
        
        return old_health - self.health
    
    def restore_energy(self, amount: int) -> int:
        """
        Restore energy to the player.
        
        Args:
            amount: Amount of energy to restore
            
        Returns:
            int: Actual amount restored
        """
        old_energy = self.energy
        self.energy = min(self.max_energy, self.energy + amount)
        return self.energy - old_energy
    
    def use_energy(self, amount: int) -> bool:
        """
        Use energy for an action.
        
        Args:
            amount: Amount of energy to use
            
        Returns:
            bool: True if player had enough energy
        """
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False
    
    def add_effect(self, effect_name: str, duration: int, properties: Dict[str, Any]) -> None:
        """
        Add a temporary effect to the player.
        
        Args:
            effect_name: Name of the effect
            duration: Duration in game minutes
            properties: Effect properties
        """
        self.effects[effect_name] = {
            "duration": duration,
            "properties": properties,
            "start_time": self.game_time
        }
    
    def remove_effect(self, effect_name: str) -> bool:
        """
        Remove an effect from the player.
        
        Args:
            effect_name: Name of the effect to remove
            
        Returns:
            bool: True if effect was removed
        """
        if effect_name in self.effects:
            del self.effects[effect_name]
            return True
        return False
    
    def update_effects(self) -> List[str]:
        """
        Update all active effects and remove expired ones.
        
        Returns:
            List of expired effect names
        """
        expired_effects = []
        
        for effect_name, effect_data in list(self.effects.items()):
            elapsed_time = self.game_time - effect_data["start_time"]
            if elapsed_time >= effect_data["duration"]:
                expired_effects.append(effect_name)
                del self.effects[effect_name]
        
        return expired_effects
    
    def get_status_display(self) -> str:
        """
        Get a formatted display of player status.
        
        Returns:
            str: Formatted status display
        """
        lines = [f"=== {self.name} ==="]
        lines.append(f"Health: {self.health}/{self.max_health}")
        lines.append(f"Energy: {self.energy}/{self.max_energy}")
        lines.append(f"Level: {self.stats['level']} (XP: {self.stats['experience']})")
        
        # Show equipped items
        equipped_items = [item for item in self.equipment.values() if item]
        if equipped_items:
            lines.append(f"Equipped: {', '.join(str(item) for item in equipped_items)}")
        
        # Show active effects
        if self.effects:
            effect_names = list(self.effects.keys())
            lines.append(f"Effects: {', '.join(effect_names)}")
        
        return "\n".join(lines)
    
    def get_stats_display(self) -> str:
        """
        Get a formatted display of player statistics.
        
        Returns:
            str: Formatted stats display
        """
        lines = [f"=== {self.name}'s Statistics ==="]
        for stat_name, value in self.stats.items():
            lines.append(f"{stat_name.capitalize()}: {value}")
        
        lines.append(f"\nRooms visited: {len(self.rooms_visited)}")
        lines.append(f"Items found: {len(self.items_found)}")
        lines.append(f"Actions taken: {self.actions_taken}")
        lines.append(f"Game time: {self.game_time} minutes")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert player to dictionary for saving.
        
        Returns:
            Dict representation of the player
        """
        return {
            "name": self.name,
            "current_room": self.current_room,
            "inventory": [item.to_dict() for item in self.inventory],
            "health": self.health,
            "max_health": self.max_health,
            "energy": self.energy,
            "max_energy": self.max_energy,
            "stats": self.stats.copy(),
            "effects": self.effects.copy(),
            "equipment": {k: v.to_dict() if v else None for k, v in self.equipment.items()},
            "rooms_visited": list(self.rooms_visited),
            "items_found": list(self.items_found),
            "actions_taken": self.actions_taken,
            "game_time": self.game_time,
            "is_alive": self.is_alive,
            "has_light_source": self.has_light_source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """
        Create player from dictionary data.
        
        Args:
            data: Dictionary containing player data
            
        Returns:
            Player instance created from the data
        """
        player = cls(data["name"], data["current_room"])
        
        # Restore inventory
        player.inventory.clear()
        for item_data in data.get("inventory", []):
            item = Item.from_dict(item_data)
            player.inventory.append(item)
        
        # Restore stats and state
        player.health = data.get("health", player.health)
        player.max_health = data.get("max_health", player.max_health)
        player.energy = data.get("energy", player.energy)
        player.max_energy = data.get("max_energy", player.max_energy)
        player.stats.update(data.get("stats", {}))
        player.effects.update(data.get("effects", {}))
        
        # Restore equipment
        equipment_data = data.get("equipment", {})
        for slot, item_data in equipment_data.items():
            if item_data:
                player.equipment[slot] = Item.from_dict(item_data)
        
        # Restore progress tracking
        player.rooms_visited = set(data.get("rooms_visited", [player.current_room]))
        player.items_found = set(data.get("items_found", []))
        player.actions_taken = data.get("actions_taken", 0)
        player.game_time = data.get("game_time", 0)
        player.is_alive = data.get("is_alive", True)
        player.has_light_source = data.get("has_light_source", False)
        
        return player
