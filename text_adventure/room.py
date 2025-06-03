class Room:
    """
    Represents a room in the text adventure game.

    Attributes:
        name (str): The name of the room.
        description (str): A description of the room.
        exits (dict): A dictionary mapping exit directions (e.g., "north")
                      to the names of connected rooms.
    """
    def __init__(self, name, description):
        """
        Initializes a new Room instance.

        Args:
            name (str): The name of the room.
            description (str): A description of the room.
        """
        self.name = name
        self.description = description
        self.exits = {}  # e.g., {"north": "kitchen"}

    def __str__(self):
        """
        Returns the string representation of the room (its name).
        """
        return self.name

    def add_exit(self, direction, room_name):
        """
        Adds an exit to the room.

        Args:
            direction (str): The direction of the exit (e.g., "north", "south").
            room_name (str): The name of the room this exit leads to.
        """
        self.exits[direction] = room_name

    def get_exit(self, direction):
        """
        Returns the room name for a given exit direction.

        Args:
            direction (str): The direction of the desired exit.

        Returns:
            str or None: The name of the room in that direction, or None if no exit exists.
        """
        return self.exits.get(direction)

    def describe(self):
        """Prints the room's description and available exits."""
        print(self.description)
        if self.exits:
            print("Exits:")
            # Print each available exit direction
            for direction in self.exits:
                print(f"- {direction}")
        else:
            print("There are no obvious exits.")
