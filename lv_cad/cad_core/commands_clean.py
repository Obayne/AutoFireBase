from __future__ import annotations


class CADCommand:
    """Base class for CAD commands that support execute/undo/redo.

    Subclasses should override :meth:`execute` and :meth:`undo`.
    """

    def __init__(self, description: str = "") -> None:
        self.description = description

    def execute(self) -> bool:
        """Execute the command. Return True on success."""
        return True

    def undo(self) -> bool:
        """Undo the command. Return True on success."""
        return True


class CADCommandStack:
    """Simple undo/redo stack for :class:`CADCommand` instances.

    This implementation is intentionally small and has only the
    operations used by the UI: execute, undo, redo, clear, and
    helpers to query the next undo/redo descriptions.
    """

    def __init__(self, max_size: int = 100) -> None:
        self.commands: list[CADCommand] = []
        self.current_index: int = -1
        self.max_size: int = max_size

    def execute(self, command: CADCommand) -> bool:
        """Execute a command and push it onto the stack if successful.

        Returns True when the command executed and was stored in the
        stack, False otherwise.
        """
        if command is None:
            return False
        if command.execute():
            # truncate any redo history
            self.commands = self.commands[: self.current_index + 1]
            self.commands.append(command)
            self.current_index += 1
            # enforce max size
            if len(self.commands) > self.max_size:
                # drop the oldest
                self.commands.pop(0)
                self.current_index -= 1
            return True
        return False

    def undo(self) -> bool:
        """Undo the last command if available."""
        if self.can_undo():
            cmd = self.commands[self.current_index]
            ok = cmd.undo()
            if ok:
                self.current_index -= 1
            return ok
        return False

    def redo(self) -> bool:
        """Redo the next command if available."""
        if self.can_redo():
            self.current_index += 1
            cmd = self.commands[self.current_index]
            return cmd.execute()
        return False

    def can_undo(self) -> bool:
        return self.current_index >= 0

    def can_redo(self) -> bool:
        return self.current_index < len(self.commands) - 1

    def clear(self) -> None:
        self.commands.clear()
        self.current_index = -1

    def get_undo_description(self) -> str | None:
        if self.can_undo():
            return self.commands[self.current_index].description
        return None

    def get_redo_description(self) -> str | None:
        if self.can_redo():
            return self.commands[self.current_index + 1].description
        return None
