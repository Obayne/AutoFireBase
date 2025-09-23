with open('app/main.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'self.scene.clearSelection()' in line:
            print(f'Found at line {i+1}: {line.strip()}')