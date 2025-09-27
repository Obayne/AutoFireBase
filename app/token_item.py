from PySide6 import QtGui, QtWidgets


class TokenItem(QtWidgets.QGraphicsSimpleTextItem):
    def __init__(self, token_string: str, device_item: QtWidgets.QGraphicsItem, parent=None):
        super().__init__(token_string, parent)
        self.token_string = token_string
        self.device_item = device_item

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations
        )  # Keep text size constant

        # Set a default font and color
        font = QtGui.QFont("Arial", 8)
        self.setFont(font)
        self.setBrush(QtGui.QBrush(QtGui.QColor("#FFFFFF")))  # Default to white

        # Set initial text
        self.setText(token_string)

    def to_json(self):
        # Simplified JSON representation
        return {
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
            "token_string": self.token_string,
        }

    @staticmethod
    def from_json(data, device_map):
        # Simplified reconstruction
        # In a real implementation, this would need more context
        return None
