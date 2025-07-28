"""
Room system for Text Adventure Game.
Represents locations in the game world with enhanced functionality.
"""

from typing import Dict, List, Any, Optional, Set
from config.game_data import get_room_data, ROOM_BEHAVIORS
from entities.item import Item, create_item


class Room:
    """
    Represents a room/location in the game world.
    
    Attributes:
        room_id (str): Unique identifier for the room
        name (str): Display name of the room
        description (str): Short description of the room
        long_description (str): Detailed description for first visits
        exits (Dict[str, str]): Available exits and their destinations
        items (List[Item]): Items present in the room
        visited (bool): Whether the player has been here before
        dark (bool): Whether the room is dark
        locked (bool): Whether the room is locked
        unlock_item (str): Item needed to unlock the room
        requires_light (bool): Whether light is needed to see properly
    """
    
    def __init__(self, room_id: str):
        """
        Initialize a room from game data.
        
        Args:
            room_id: The unique identifier for this room
        """
        self.room_id = room_id
        room_data = get_room_data(room_id)
        
        if not room_data:
            raise ValueError(f"Unknown room ID: {room_id}")
        
        # Basic properties
        self.name = room_data["name"]
        self.description = room_data["description"]
        self.long_description = room_data.get("long_description", self.description)
        self.exits = room_data.get("exits", {}).copy()
        
        # State properties
        self.visited = room_data.get("visited", False)
        self.dark = room_data.get("dark", False)
        self.locked = room_data.get("locked", False)
        self.unlock_item = room_data.get("unlock_item")
        self.requires_light = room_data.get("requires_light", False)
        
        # Initialize items from room data
        self.items: List[Item] = []
        for item_id in room_data.get("items", []):
            item = create_item(item_id)
            if item:
                self.items.append(item)
        
        # Additional properties for extensibility
        self.properties = {k: v for k, v in room_data.items() 
                          if k not in ["name", "description", "long_description", 
                                     "exits", "items", "visited", "dark", "locked", 
                                     "unlock_item", "requires_light"]}
        
        # Dynamic state
        self.lit = not self.dark  # Whether the room is currently lit
        self.unlocked = not self.locked  # Whether the room is currently unlocked
        self.npcs: List[Any] = []  # NPCs in the room (for future expansion)
        self.special_features: Set[str] = set()  # Special room features
    
    def __str__(self) -> str:
        """Return string representation of the room."""
        return self.name
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return f"Room(id='{self.room_id}', name='{self.name}', visited={self.visited})"
    
    def get_description(self, player_has_light: bool = False) -> str:
        """
        Get the appropriate description for the room.
        
        Args:
            player_has_light: Whether the player has a light source
            
        Returns:
            str: Room description based on current state
        """
        # Check if room can be seen
        if self.dark and not (self.lit or player_has_light):
            return "It's too dark to see anything clearly. You need a source of light."
        
        # Use long description for first visit, short for subsequent visits
        if not self.visited:
            description = self.long_description
        else:
            description = self.description
        
        # Add items description if any are visible
        if self.items:
            item_names = [str(item) for item in self.items]
            if len(item_names) == 1:
                description += f"\n\nYou see {item_names[0]} here."
            else:
                description += f"\n\nYou see the following items: {', '.join(item_names)}."
        
        # Add exits description
        if self.exits:
            exit_list = list(self.exits.keys())
            if len(exit_list) == 1:
                description += f"\n\nThere is an exit to the {exit_list[0]}."
            else:
                description += f"\n\nExits are: {', '.join(exit_list)}."
        
        return description
    
    def describe(self, player_has_light: bool = False) -> None:
        """
        Print the room description.
        
        Args:
            player_has_light: Whether the player has a light source
        """
        print(f"\n=== {self.name} ===")
        print(self.get_description(player_has_light))
        
        # Mark as visited
        if not self.visited:
            self.visited = True
    
    def add_exit(self, direction: str, room_id: str) -> None:
        """
        Add an exit to the room.
        
        Args:
            direction: Direction of the exit
            room_id: ID of the destination room
        """
        self.exits[direction] = room_id
    
    def remove_exit(self, direction: str) -> bool:
        """
        Remove an exit from the room.
        
        Args:
            direction: Direction of the exit to remove
            
        Returns:
            bool: True if exit was removed, False if it didn't exist
        """
        if direction in self.exits:
            del self.exits[direction]
            return True
        return False
    
    def get_exit(self, direction: str) -> Optional[str]:
        """
        Get the destination room for a given direction.
        
        Args:
            direction: Direction to check
            
        Returns:
            str: Room ID of destination, or None if no exit exists
        """
        return self.exits.get(direction.lower())
    
    def can_enter(self, player_inventory: List[Item]) -> tuple[bool, str]:
        """
        Check if the room can be entered.
        
        Args:
            player_inventory: Player's current inventory
            
        Returns:
            Tuple of (can_enter, reason_if_not)
        """
        if self.locked and not self.unlocked:
            if not self.unlock_item:
                return False, "This room is locked and cannot be opened."
            
            # Check if player has the required item
            has_key = any(item.item_id == self.unlock_item for item in player_inventory)
            if not has_key:
                return False, f"This room is locked. You need a {self.unlock_item} to enter."
        
        return True, ""
    
    def unlock_with_item(self, item: Item) -> bool:
        """
        Attempt to unlock the room with an item.
        
        Args:
            item: Item to use for unlocking
            
        Returns:
            bool: True if room was unlocked
        """
        if not self.locked or self.unlocked:
            return False
        
        if self.unlock_item and item.item_id == self.unlock_item:
            self.unlocked = True
            
            # Execute special behavior if defined
            behavior = ROOM_BEHAVIORS.get(self.room_id, {})
            if "on_unlock" in behavior:
                print(behavior["on_unlock"])
            
            return True
        
        return False
    
    def light_room(self) -> None:
        """Light up the room if it's dark."""
        if self.dark:
            self.lit = True
            
            # Execute special behavior if defined
            behavior = ROOM_BEHAVIORS.get(self.room_id, {})
            if "on_enter_lit" in behavior:
                print(behavior["on_enter_lit"])
    
    def add_item(self, item: Item) -> None:
        """
        Add an item to the room.
        
        Args:
            item: Item to add to the room
        """
        # Try to combine with existing items of the same type
        for existing_item in self.items:
            if existing_item.item_id == item.item_id:
                if existing_item.combine_with(item):
                    return
        
        # If no combination possible, add as new item
        self.items.append(item)
    
    def remove_item(self, item: Item) -> bool:
        """
        Remove an item from the room.
        
        Args:
            item: Item to remove
            
        Returns:
            bool: True if item was removed
        """
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def find_item(self, keyword: str) -> Optional[Item]:
        """
        Find an item in the room by keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            Item if found, None otherwise
        """
        for item in self.items:
            if item.matches_keyword(keyword):
                return item
        return None
    
    def get_items_by_type(self, item_type: str) -> List[Item]:
        """
        Get all items of a specific type in the room.
        
        Args:
            item_type: Type of items to find
            
        Returns:
            List of matching items
        """
        return [item for item in self.items if item.item_id == item_type]
    
    def has_items(self) -> bool:
        """Check if the room has any items."""
        return len(self.items) > 0
    
    def get_item_count(self) -> int:
        """Get the total number of items in the room."""
        return sum(item.quantity for item in self.items)
    
    def add_special_feature(self, feature: str) -> None:
        """
        Add a special feature to the room.
        
        Args:
            feature: Name of the special feature
        """
        self.special_features.add(feature)
    
    def remove_special_feature(self, feature: str) -> bool:
        """
        Remove a special feature from the room.
        
        Args:
            feature: Name of the feature to remove
            
        Returns:
            bool: True if feature was removed
        """
        if feature in self.special_features:
            self.special_features.remove(feature)
            return True
        return False
    
    def has_special_feature(self, feature: str) -> bool:
        """
        Check if the room has a specific special feature.
        
        Args:
            feature: Name of the feature to check
            
        Returns:
            bool: True if room has the feature
        """
        return feature in self.special_features
    
    def reset_to_initial_state(self) -> None:
        """Reset the room to its initial state."""
        room_data = get_room_data(self.room_id)
        if room_data:
            self.visited = room_data.get("visited", False)
            self.lit = not room_data.get("dark", False)
            self.unlocked = not room_data.get("locked", False)
            
            # Reset items
            self.items.clear()
            for item_id in room_data.get("items", []):
                item = create_item(item_id)
                if item:
                    self.items.append(item)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert room to dictionary for saving.
        
        Returns:
            Dict representation of the room
        """
        return {
            "room_id": self.room_id,
            "visited": self.visited,
            "lit": self.lit,
            "unlocked": self.unlocked,
            "items": [item.to_dict() for item in self.items],
            "special_features": list(self.special_features),
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Room':
        """
        Create room from dictionary data.
        
        Args:
            data: Dictionary containing room data
            
        Returns:
            Room instance created from the data
        """
        room = cls(data["room_id"])
        room.visited = data.get("visited", False)
        room.lit = data.get("lit", not room.dark)
        room.unlocked = data.get("unlocked", not room.locked)
        
        # Restore items
        room.items.clear()
        for item_data in data.get("items", []):
            item = Item.from_dict(item_data)
            room.items.append(item)
        
        # Restore special features
        room.special_features = set(data.get("special_features", []))
        room.properties.update(data.get("properties", {}))
        
        return room


def create_room(room_id: str) -> Optional[Room]:
    """
    Factory function to create a room.
    
    Args:
        room_id: The ID of the room to create
        
    Returns:
        Room instance or None if room_id is invalid
    """
    try:
        return Room(room_id)
    except ValueError:
        return None
