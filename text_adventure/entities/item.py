"""
Item system for Text Adventure Game.
Represents items that can be found, carried, and used by the player.
"""

from typing import Dict, List, Any, Optional
from config.game_data import get_item_data


class Item:
    """
    Represents an item in the game world.
    
    Attributes:
        item_id (str): Unique identifier for the item type
        name (str): Display name of the item
        description (str): Detailed description of the item
        weight (int): Weight of the item (affects inventory capacity)
        value (int): Monetary value of the item
        usable (bool): Whether the item can be used
        consumable (bool): Whether the item is consumed when used
        keywords (List[str]): Keywords for item recognition
        properties (Dict[str, Any]): Additional item properties
    """
    
    def __init__(self, item_id: str):
        """
        Initialize an item from game data.
        
        Args:
            item_id: The unique identifier for this item type
        """
        self.item_id = item_id
        item_data = get_item_data(item_id)
        
        if not item_data:
            raise ValueError(f"Unknown item ID: {item_id}")
        
        # Basic properties
        self.name = item_data["name"]
        self.description = item_data["description"]
        self.weight = item_data.get("weight", 1)
        self.value = item_data.get("value", 0)
        self.usable = item_data.get("usable", False)
        self.consumable = item_data.get("consumable", False)
        self.keywords = item_data.get("keywords", [])
        
        # Special properties
        self.weapon = item_data.get("weapon", False)
        self.damage = item_data.get("damage", 0)
        self.effect = item_data.get("effect", {})
        
        # Additional properties for extensibility
        self.properties = {k: v for k, v in item_data.items() 
                          if k not in ["name", "description", "weight", "value", 
                                     "usable", "consumable", "keywords", "weapon", 
                                     "damage", "effect"]}
        
        # Instance-specific state
        self.quantity = 1
        self.condition = 100  # 0-100, affects effectiveness
        self.identified = True  # Whether player knows what this item is
    
    def __str__(self) -> str:
        """Return string representation of the item."""
        if self.quantity > 1:
            return f"{self.name} (x{self.quantity})"
        return self.name
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return f"Item(id='{self.item_id}', name='{self.name}', qty={self.quantity})"
    
    def matches_keyword(self, keyword: str) -> bool:
        """
        Check if the item matches a given keyword.
        
        Args:
            keyword: The keyword to check against
            
        Returns:
            bool: True if the item matches the keyword
        """
        keyword_lower = keyword.lower()
        
        # Check exact name match
        if keyword_lower in self.name.lower():
            return True
        
        # Check keywords list
        return any(keyword_lower in kw.lower() for kw in self.keywords)
    
    def can_use(self) -> bool:
        """
        Check if the item can be used.
        
        Returns:
            bool: True if the item can be used
        """
        return self.usable and self.condition > 0
    
    def use(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Use the item and return the result.
        
        Args:
            context: Optional context information for item use
            
        Returns:
            Dict containing the result of using the item
        """
        if not self.can_use():
            return {
                "success": False,
                "message": f"You can't use the {self.name} right now.",
                "consumed": False
            }
        
        result = {
            "success": True,
            "message": f"You use the {self.name}.",
            "consumed": self.consumable,
            "effects": self.effect.copy() if self.effect else {}
        }
        
        # Apply condition degradation for non-consumable items
        if not self.consumable:
            self.condition = max(0, self.condition - 5)
            if self.condition <= 0:
                result["message"] += f" The {self.name} breaks from use!"
        
        # Handle special item behaviors
        if self.item_id == "lamp":
            result["message"] = f"You light the {self.name}. It casts a warm glow around you."
            result["effects"]["provides_light"] = True
        elif self.item_id == "potion":
            result["message"] = f"You drink the {self.name}. You feel refreshed!"
        elif self.item_id == "book":
            result["message"] = f"You read from the {self.name}. Ancient knowledge fills your mind."
        elif self.item_id == "key":
            result["message"] = f"You hold the {self.name}, ready to unlock something."
        elif self.item_id == "sword":
            result["message"] = f"You brandish the {self.name}. You feel more confident."
            result["effects"]["weapon_equipped"] = True
        
        return result
    
    def examine(self) -> str:
        """
        Get a detailed examination of the item.
        
        Returns:
            str: Detailed description of the item
        """
        examination = self.description
        
        # Add condition information
        if self.condition < 100:
            if self.condition > 75:
                examination += " It shows slight signs of wear."
            elif self.condition > 50:
                examination += " It's somewhat worn but still functional."
            elif self.condition > 25:
                examination += " It's quite worn and may not last much longer."
            else:
                examination += " It's in very poor condition and barely functional."
        
        # Add special properties
        if self.weapon:
            examination += f" It appears to be a weapon that could deal {self.damage} damage."
        
        if self.effect:
            examination += " It seems to have special properties."
        
        # Add weight and value if significant
        if self.weight > 3:
            examination += f" It's quite heavy ({self.weight} units)."
        
        if self.value > 50:
            examination += f" It looks valuable (worth about {self.value} gold)."
        
        return examination
    
    def get_weight(self) -> int:
        """
        Get the total weight of this item stack.
        
        Returns:
            int: Total weight considering quantity
        """
        return self.weight * self.quantity
    
    def get_value(self) -> int:
        """
        Get the total value of this item stack.
        
        Returns:
            int: Total value considering quantity and condition
        """
        base_value = self.value * self.quantity
        condition_modifier = self.condition / 100.0
        return int(base_value * condition_modifier)
    
    def split(self, amount: int) -> Optional['Item']:
        """
        Split a quantity from this item stack.
        
        Args:
            amount: Number of items to split off
            
        Returns:
            New Item instance with the split quantity, or None if invalid
        """
        if amount <= 0 or amount >= self.quantity:
            return None
        
        # Create new item with split quantity
        new_item = Item(self.item_id)
        new_item.quantity = amount
        new_item.condition = self.condition
        new_item.identified = self.identified
        
        # Reduce this item's quantity
        self.quantity -= amount
        
        return new_item
    
    def combine_with(self, other: 'Item') -> bool:
        """
        Combine this item with another of the same type.
        
        Args:
            other: Another item to combine with
            
        Returns:
            bool: True if combination was successful
        """
        if (self.item_id != other.item_id or 
            abs(self.condition - other.condition) > 10):
            return False
        
        # Combine quantities and average condition
        total_quantity = self.quantity + other.quantity
        avg_condition = ((self.condition * self.quantity + 
                         other.condition * other.quantity) / total_quantity)
        
        self.quantity = total_quantity
        self.condition = int(avg_condition)
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert item to dictionary for saving.
        
        Returns:
            Dict representation of the item
        """
        return {
            "item_id": self.item_id,
            "quantity": self.quantity,
            "condition": self.condition,
            "identified": self.identified,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """
        Create item from dictionary data.
        
        Args:
            data: Dictionary containing item data
            
        Returns:
            Item instance created from the data
        """
        item = cls(data["item_id"])
        item.quantity = data.get("quantity", 1)
        item.condition = data.get("condition", 100)
        item.identified = data.get("identified", True)
        item.properties.update(data.get("properties", {}))
        return item


def create_item(item_id: str, quantity: int = 1) -> Optional[Item]:
    """
    Factory function to create an item.
    
    Args:
        item_id: The ID of the item to create
        quantity: Number of items to create
        
    Returns:
        Item instance or None if item_id is invalid
    """
    try:
        item = Item(item_id)
        item.quantity = quantity
        return item
    except ValueError:
        return None


def find_item_by_keyword(items: List[Item], keyword: str) -> Optional[Item]:
    """
    Find an item in a list by keyword.
    
    Args:
        items: List of items to search
        keyword: Keyword to search for
        
    Returns:
        First matching item or None
    """
    for item in items:
        if item.matches_keyword(keyword):
            return item
    return None
