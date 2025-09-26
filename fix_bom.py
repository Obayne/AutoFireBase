# Fix BOM issue in main.py
with open("c:\\Dev\\Autofire\\app\\main.py", "rb") as f:
    content = f.read()

# Remove BOM if present
if content.startswith(b"\xef\xbb\xbf"):
    content = content[3:]

with open("c:\\Dev\\Autofire\\app\\main_fixed.py", "wb") as out:
    out.write(content)
