from PySide6 import QtWidgets, QtCore, QtGui

class TokenItem(QtWidgets.QGraphicsSimpleTextItem):
    def __init__(self, token_string: str, device_item: QtWidgets.QGraphicsItem, parent=None):
        super().__init__(token_string, parent)
        self.token_string = token_string
        self.device_item = device_item

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations) # Keep text size constant

        # Set a default font and color
        font = QtGui.QFont("Arial", 8)
        self.setFont(font)
        self.setBrush(QtGui.QBrush(QtGui.QColor("#FFFFFF"))) # Default to white

        self.update_token_text()

    def update_token_text(self):
        # Extract the attribute name from the token string (e.g., "name" from "{name}")
        attr_name = self.token_string.strip("{}")
        
        # Get the value from the associated device_item
        value = getattr(self.device_item, attr_name, "N/A")
        
        # Control visibility based on layer properties
        is_visible = True
        if self.device_item.layer:
            layer_props = self.device_item.layer
            if attr_name == "slc_address":
                is_visible = layer_props.get('show_slc_address', True)
            elif attr_name == "circuit_id":
                is_visible = layer_props.get('show_circuit_id', True)
            elif attr_name == "zone":
                is_visible = layer_props.get('show_zone', True)
            elif attr_name == "max_current_ma":
                is_visible = layer_props.get('show_max_current_ma', True)
            elif attr_name == "voltage_v":
                is_visible = layer_props.get('show_voltage_v', True)
            elif attr_name == "addressable":
                is_visible = layer_props.get('show_addressable', True)
            elif attr_name == "candela_options":
                is_visible = layer_props.get('show_candela_options', True)
            elif attr_name == "name":
                is_visible = layer_props.get('show_name', True)
            elif attr_name == "part_number":
                is_visible = layer_props.get('show_part_number', True)

        self.setVisible(is_visible)

        # Special handling for certain attributes
        if attr_name == "part_number":
            value = self.device_item.part_number # Use the stored part_number
        elif attr_name == "manufacturer":
            value = self.device_item.manufacturer # Use the stored manufacturer
        elif attr_name == "device_type":
            value = self.device_item.device_type # Use the stored device_type
        elif attr_name == "layer_name":
            value = self.device_item.layer['name'] if self.device_item.layer else "N/A"
        elif attr_name == "slc_address":
            value = str(self.device_item.slc_address) if self.device_item.slc_address is not None else "N/A"
        elif attr_name == "circuit_id":
            value = str(self.device_item.circuit_id) if self.device_item.circuit_id is not None else "N/A"
        elif attr_name == "zone":
            value = self.device_item.zone if self.device_item.zone else "N/A"
        elif attr_name == "max_current_ma":
            # This would require fetching from fire_alarm_device_specs table
            value = "N/A" # Placeholder
        elif attr_name == "voltage_v":
            value = "N/A" # Placeholder
        elif attr_name == "addressable":
            value = "N/A" # Placeholder
        elif attr_name == "candela_options":
            value = ", ".join(map(str, self.device_item.coverage.get("candelas", []))) if self.device_item.coverage.get("candelas") else "N/A"

        self.setText(str(value))

    def to_json(self):
        return {
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
            "token_string": self.token_string,
            "device_id": self.device_item.data(0, QtCore.Qt.UserRole) # Assuming device_item stores its ID
        }

    @staticmethod
    def from_json(data, device_map): # device_map will be a dict of device_id to DeviceItem
        device_id = data.get("device_id")
        device_item = device_map.get(device_id)
        if device_item:
            token_item = TokenItem(data["token_string"], device_item)
            token_item.setPos(float(data.get("x",0)), float(data.get("y",0)))
            return token_item
        return None
