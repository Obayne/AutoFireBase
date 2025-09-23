# Script to remove BOM from main.py comprehensively
# Read the file in binary mode to see exactly what's there
with open('app/main.py', 'rb') as f:
    content = f.read()

# Check if it starts with BOM
if content.startswith(b'\xef\xbb\xbf'):
    # Remove the BOM
    content = content[3:]
    print("BOM found and removed")
else:
    print("No BOM found at the beginning")

# Write the file back without BOM
with open('app/main.py', 'wb') as f:
    f.write(content)

print("File saved without BOM")