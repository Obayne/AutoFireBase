f1 = open('c:/Dev/Autofire/app/main.py', 'rb').read()
f2 = open('c:/Dev/Autofire/app/main_final.py', 'rb').read()
print('Files are identical' if f1 == f2 else 'Files are different')