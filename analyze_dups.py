import re

# Read the main.py file
with open('app/main.py', 'r', encoding='utf-16') as f:
    content = f.read()

# Find all class definitions
class_pattern = r'class (\w+)'
classes = re.findall(class_pattern, content)
print('Classes found:', classes)

# Find all method definitions with their line numbers
method_pattern = r'^\s*def (\w+)\('
method_lines = []
lines = content.split('\n')
for i, line in enumerate(lines):
    match = re.match(method_pattern, line)
    if match:
        method_lines.append((match.group(1), i+1))

# Group methods by name
method_groups = {}
for method_name, line_num in method_lines:
    if method_name not in method_groups:
        method_groups[method_name] = []
    method_groups[method_name].append(line_num)

# Find duplicated methods
duplicated_methods = {name: lines for name, lines in method_groups.items() if len(lines) > 1}
print('Duplicated methods with line numbers:', duplicated_methods)

# Look for specific patterns that might indicate duplication
init_count = len([name for name in method_groups.keys() if name == '__init__'])
apply_count = len([name for name in method_groups.keys() if name == 'apply'])
print(f"Number of __init__ methods: {init_count}")
print(f"Number of apply methods: {apply_count}")