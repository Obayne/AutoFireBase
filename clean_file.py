# Script to clean the main.py file thoroughly
with open('app/main.py', 'rb') as f:
    content = f.read()

# Count how many BOM markers we have at the beginning
bom_count = 0
while content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
    bom_count += 1

print(f"Removed {bom_count} BOM markers")

# Now read as text and write back properly
content_text = content.decode('utf-8')

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content_text)

print("File cleaned and saved properly")