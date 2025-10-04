"""
CAD Commands - Undo/Redo system for CAD operations
"""

from abc import ABC, abstractmethod


class CADCommand(ABC):
    """Base class for CAD commands that support undo/redo."""

    def __init__(self, description: str):
        self.description = description

    @abstractmethod
    def execute(self) -> bool:
        """Execute the command. Returns True if successful."""
        pass

    @abstractmethod
    def undo(self) -> bool:
        """Undo the command. Returns True if successful."""
        pass

    @abstractmethod
    def redo(self) -> bool:
        """Redo the command. Returns True if successful."""
        pass


class AddDeviceCommand(CADCommand):
    """Command for adding a device to the scene."""

    def __init__(self, scene, device_item, layer_group):
        super().__init__(f"Add {device_item.name}")
        self.scene = scene
        self.device_item = device_item
        self.layer_group = layer_group

    def execute(self) -> bool:
        self.layer_group.addToGroup(self.device_item)
        return True

    def undo(self) -> bool:
        if self.device_item.scene() == self.scene:
            self.scene.removeItem(self.device_item)
            return True
        return False

    def redo(self) -> bool:
        return self.execute()


class DeleteDeviceCommand(CADCommand):
    """Command for deleting a device from the scene."""

    def __init__(self, scene, device_item, layer_group):
        super().__init__(f"Delete {getattr(device_item, 'name', 'device')}")
        self.scene = scene
        self.device_item = device_item
        self.layer_group = layer_group
        self.parent_item = device_item.parentItem()

    def execute(self) -> bool:
        if self.device_item.scene() == self.scene:
            self.scene.removeItem(self.device_item)
            return True
        return False

    def undo(self) -> bool:
        if self.parent_item:
            self.parent_item.addToGroup(self.device_item)
        else:
            self.scene.addItem(self.device_item)
        return True

    def redo(self) -> bool:
        return self.execute()


class MoveDeviceCommand(CADCommand):
    """Command for moving a device."""

    def __init__(self, device_item, old_pos, new_pos):
        super().__init__(f"Move {getattr(device_item, 'name', 'device')}")
        self.device_item = device_item
        self.old_pos = old_pos
        self.new_pos = new_pos

    def execute(self) -> bool:
        self.device_item.setPos(self.new_pos)
        return True

    def undo(self) -> bool:
        self.device_item.setPos(self.old_pos)
        return True

    def redo(self) -> bool:
        return self.execute()


class CADCommandStack:
    """Stack for managing undo/redo commands."""

    def __init__(self, max_size: int = 50):
        self.commands: list[CADCommand] = []
        self.current_index = -1
        self.max_size = max_size

    def execute(self, command: CADCommand) -> bool:
        """Execute a command and add it to the stack."""
        if command.execute():
            # Remove any commands after current index (when doing new action after undo)
            self.commands = self.commands[: self.current_index + 1]

            # Add new command
            self.commands.append(command)
            self.current_index += 1

            # Maintain max size
            if len(self.commands) > self.max_size:
                self.commands.pop(0)
                self.current_index -= 1

            return True
        return False

    def undo(self) -> bool:
        """Undo the last command."""
        if self.can_undo():
            result = self.commands[self.current_index].undo()
            if result:
                self.current_index -= 1
            return result
        return False

    def redo(self) -> bool:
        """Redo the next command."""
        if self.can_redo():
            self.current_index += 1
            return self.commands[self.current_index].redo()
        return False

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.current_index >= 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.current_index < len(self.commands) - 1

    def get_undo_description(self) -> str:
        """Get description of the command that can be undone."""
        if self.can_undo():
            return self.commands[self.current_index].description
        return ""

    def get_redo_description(self) -> str:
        """Get description of the command that can be redone."""
        if self.can_redo():
            return self.commands[self.current_index + 1].description
        return ""

    def clear(self):
        """Clear the command stack."""
        self.commands.clear()
        self.current_index = -1
