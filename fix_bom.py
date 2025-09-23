import codecs

# Read the file without the BOM
with codecs.open('app/main.py', 'r', 'utf-8-sig') as f:
    content = f.read()

# Write it back without the BOM
with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("BOM removed successfully")