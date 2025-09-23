from app.device import DeviceItem
d = DeviceItem(0, 0, 'FACP', 'Panel', 'Generic', 'FACP-001')
print('Device created successfully')
print(f'Initial connection status: {d.connection_status}')
d.set_connection_status('connected')
print(f'After setting to connected: {d.connection_status}')
print('Test completed successfully')