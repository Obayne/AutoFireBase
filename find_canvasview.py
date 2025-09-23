with open('app/main.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'CanvasView' in line:
            print(f'Line {i+1}: {line.strip()}')