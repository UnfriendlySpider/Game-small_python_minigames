class Player:
    """Represents the player in the text adventure game."""
    def __init__(self, name, current_room):
        self.name = name
        self.inventory = []
        self.current_room = current_room

    def __str__(self):
        return self.name

    def add_to_inventory(self, item):
        """Adds an item to the player's inventory."""
        self.inventory.append(item)
        print(f"{item} added to inventory.")

    def remove_from_inventory(self, item):
        """Removes an item from the player's inventory."""
        if item in self.inventory:
            self.inventory.remove(item)
            print(f"{item} removed from inventory.")
        else:
            print(f"{item} not found in inventory.")

    def move(self, room):
        """Moves the player to a new room."""
        self.current_room = room
