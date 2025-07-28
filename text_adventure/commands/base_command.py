"""
Base command system for Text Adventure Game.
Provides the foundation for all game commands.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseCommand(ABC):
    """
    Abstract base class for all game commands.
    
    All commands must inherit from this class and implement the execute method.
    """
    
    def __init__(self, name: str, aliases: Optional[List[str]] = None, 
                 description: str = "", help_text: str = ""):
        """
        Initialize a command.
        
        Args:
            name: Primary name of the command
            aliases: Alternative names for the command
            description: Short description of what the command does
            help_text: Detailed help text for the command
        """
        self.name = name.lower()
        self.aliases = [alias.lower() for alias in (aliases or [])]
        self.description = description
        self.help_text = help_text or description
        
        # All possible names for this command
        self.all_names = [self.name] + self.aliases
    
    def matches(self, command_name: str) -> bool:
        """
        Check if this command matches the given name.
        
        Args:
            command_name: Name to check against
            
        Returns:
            bool: True if this command matches the name
        """
        return command_name.lower() in self.all_names
    
    @abstractmethod
    def execute(self, args: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the command.
        
        Args:
            args: List of arguments passed to the command
            game_state: Current game state dictionary
            
        Returns:
            Dict containing the result of the command execution
        """
        pass
    
    def get_usage(self) -> str:
        """
        Get usage information for the command.
        
        Returns:
            str: Usage information
        """
        return f"{self.name}: {self.description}"
    
    def get_help(self) -> str:
        """
        Get detailed help for the command.
        
        Returns:
            str: Detailed help text
        """
        help_lines = [f"Command: {self.name}"]
        
        if self.aliases:
            help_lines.append(f"Aliases: {', '.join(self.aliases)}")
        
        help_lines.append(f"Description: {self.help_text}")
        
        return "\n".join(help_lines)
    
    def validate_args(self, args: List[str], min_args: int = 0, 
                     max_args: Optional[int] = None) -> tuple[bool, str]:
        """
        Validate command arguments.
        
        Args:
            args: Arguments to validate
            min_args: Minimum number of arguments required
            max_args: Maximum number of arguments allowed (None for unlimited)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(args) < min_args:
            return False, f"Not enough arguments. Expected at least {min_args}."
        
        if max_args is not None and len(args) > max_args:
            return False, f"Too many arguments. Expected at most {max_args}."
        
        return True, ""
    
    def __str__(self) -> str:
        """Return string representation of the command."""
        return self.name
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return f"Command(name='{self.name}', aliases={self.aliases})"


class CommandResult:
    """
    Represents the result of executing a command.
    """
    
    def __init__(self, success: bool = True, message: str = "", 
                 data: Optional[Dict[str, Any]] = None, 
                 state_change: Optional[str] = None):
        """
        Initialize a command result.
        
        Args:
            success: Whether the command executed successfully
            message: Message to display to the player
            data: Additional data from command execution
            state_change: Requested state change (if any)
        """
        self.success = success
        self.message = message
        self.data = data or {}
        self.state_change = state_change
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "state_change": self.state_change
        }
    
    @classmethod
    def success_result(cls, message: str = "", data: Optional[Dict[str, Any]] = None) -> 'CommandResult':
        """Create a successful command result."""
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error_result(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'CommandResult':
        """Create an error command result."""
        return cls(success=False, message=message, data=data)
    
    @classmethod
    def state_change_result(cls, state: str, message: str = "", 
                           data: Optional[Dict[str, Any]] = None) -> 'CommandResult':
        """Create a command result that requests a state change."""
        return cls(success=True, message=message, data=data, state_change=state)


class CommandManager:
    """
    Manages all game commands and handles command execution.
    """
    
    def __init__(self):
        """Initialize the command manager."""
        self.commands: Dict[str, BaseCommand] = {}
        self.command_history: List[str] = []
        self.max_history = 50
    
    def register_command(self, command: BaseCommand) -> None:
        """
        Register a command with the manager.
        
        Args:
            command: Command to register
        """
        # Register the command under all its names
        for name in command.all_names:
            self.commands[name] = command
    
    def unregister_command(self, command_name: str) -> bool:
        """
        Unregister a command from the manager.
        
        Args:
            command_name: Name of the command to unregister
            
        Returns:
            bool: True if command was unregistered
        """
        if command_name in self.commands:
            command = self.commands[command_name]
            # Remove all names for this command
            for name in command.all_names:
                if name in self.commands:
                    del self.commands[name]
            return True
        return False
    
    def get_command(self, command_name: str) -> Optional[BaseCommand]:
        """
        Get a command by name.
        
        Args:
            command_name: Name of the command to get
            
        Returns:
            Command instance or None if not found
        """
        return self.commands.get(command_name.lower())
    
    def execute_command(self, command_line: str, game_state: Dict[str, Any]) -> CommandResult:
        """
        Execute a command from a command line string.
        
        Args:
            command_line: Full command line to execute
            game_state: Current game state
            
        Returns:
            CommandResult with the execution result
        """
        # Add to history
        self.add_to_history(command_line)
        
        # Parse command line
        parts = command_line.strip().split()
        if not parts:
            return CommandResult.error_result("Please enter a command.")
        
        command_name = parts[0].lower()
        args = parts[1:]
        
        # Find command
        command = self.get_command(command_name)
        if not command:
            return CommandResult.error_result(f"Unknown command: {command_name}")
        
        # Execute command
        try:
            result_dict = command.execute(args, game_state)
            
            # Convert dict result to CommandResult if needed
            if isinstance(result_dict, dict):
                return CommandResult(
                    success=result_dict.get("success", True),
                    message=result_dict.get("message", ""),
                    data=result_dict.get("data", {}),
                    state_change=result_dict.get("state_change")
                )
            else:
                return result_dict
                
        except Exception as e:
            return CommandResult.error_result(f"Error executing command: {str(e)}")
    
    def add_to_history(self, command: str) -> None:
        """
        Add a command to the history.
        
        Args:
            command: Command to add to history
        """
        self.command_history.append(command)
        
        # Keep history size manageable
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]
    
    def get_history(self, limit: int = 10) -> List[str]:
        """
        Get recent command history.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of recent commands
        """
        return self.command_history[-limit:] if limit > 0 else self.command_history
    
    def get_all_commands(self) -> List[BaseCommand]:
        """
        Get all registered commands (unique instances).
        
        Returns:
            List of all command instances
        """
        seen = set()
        unique_commands = []
        
        for command in self.commands.values():
            if command.name not in seen:
                unique_commands.append(command)
                seen.add(command.name)
        
        return unique_commands
    
    def get_commands_by_category(self) -> Dict[str, List[BaseCommand]]:
        """
        Get commands organized by category.
        
        Returns:
            Dict mapping category names to command lists
        """
        categories = {
            "Movement": [],
            "Actions": [],
            "Inventory": [],
            "Game": [],
            "Other": []
        }
        
        for command in self.get_all_commands():
            # Categorize based on command name/type
            if command.name in ["go", "north", "south", "east", "west", "up", "down"]:
                categories["Movement"].append(command)
            elif command.name in ["look", "examine", "get", "drop", "use"]:
                categories["Actions"].append(command)
            elif command.name in ["inventory", "status", "stats"]:
                categories["Inventory"].append(command)
            elif command.name in ["save", "load", "quit", "help"]:
                categories["Game"].append(command)
            else:
                categories["Other"].append(command)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def get_help_text(self) -> str:
        """
        Get formatted help text for all commands.
        
        Returns:
            str: Formatted help text
        """
        lines = ["Available Commands:"]
        lines.append("=" * 50)
        
        categories = self.get_commands_by_category()
        
        for category, commands in categories.items():
            lines.append(f"\n{category}:")
            for command in sorted(commands, key=lambda c: c.name):
                lines.append(f"  {command.get_usage()}")
        
        return "\n".join(lines)
