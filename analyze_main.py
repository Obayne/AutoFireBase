import re

# Read the main.py file
with open('app/main.py', 'r', encoding='utf-16') as f:
    content = f.read()

# Check for duplicated methods
methods = re.findall(r'def (\w+)\(', content)
duplicates = [m for m in set(methods) if methods.count(m) > 1]
print('Duplicated methods:', duplicates)

# Check for specific GUI elements
print('BottomBar occurrences:', content.count('BottomBar'))
print('MainWindow class occurrences:', content.count('class MainWindow'))

# Check file size and structure
print('File length:', len(content))
print('Number of lines:', len(content.splitlines()))
print('Number of def statements:', content.count('def '))
print('Number of class statements:', content.count('class '))