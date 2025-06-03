class Player:
    """
    Represents the player in the text adventure game.

    Attributes:
        name (str): The name of the player.
        inventory (list): A list of items the player is carrying.
        current_room (str): The name of the room the player is currently in.
    """
    def __init__(self, name, current_room):
        """
        Initializes a new Player instance.

        Args:
            name (str): The name of the player.
            current_room (str): The name of the room the player starts in.
        """
        self.name = name
        self.inventory = []  # Player starts with an empty inventory
        self.current_room = current_room

    def __str__(self):
        """
        Returns the string representation of the player (their name).
        """
        return self.name

    def add_to_inventory(self, item):
        """
        Adds an item to the player's inventory.

        Args:
            item (str): The item to add.
        """
        self.inventory.append(item)
        print(f"'{item}' added to inventory.")

    def remove_from_inventory(self, item):
        """
        Removes an item from the player's inventory.

        Args:
            item (str): The item to remove.
        """
        if item in self.inventory:
            self.inventory.remove(item)
            print(f"'{item}' removed from inventory.")
        else:
            print(f"'{item}' not found in inventory.")

    def move(self, room_name):
        """
        Updates the player's current room.

        Args:
            room_name (str): The name of the room the player is moving to.
        """
        self.current_room = room_name
