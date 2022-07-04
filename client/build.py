from PyInstaller.__main__ import run
import tinyaes
import random
import string
from pathlib import Path
import python_obfuscator
import pyarmor
import shutil
import re
import os

shutil.copy("main.py", "obf.py")

file_name = input("File name:\n")
file_icon = input("File icon path (NONE for no icon):\n")
build_note = input("Note (Shorter is better):\n")

with open("obf.py", "r") as f:
    script = f"""{f.read()}"""
    re.sub('\nNOTE = \".*?\" #The note returned', build_note, script, flags=re.DOTALL)
    with open ("obf.py", "w") as f:
        f.write(script)

# os.system("pyobfuscate -i obf.py -r True")
os.system("pyarmor obfuscate --exact obf.py")

with open("dist/obf.py", "r") as f:
    script = f"""{f.read()}"""
    with open ("obf.py", "w") as f:
        f.write(script)

key = ''.join(random.choices(string.ascii_letters, k=5)).encode('utf-16')
print('Key = ' + str(key))
try:
    if (file_icon != "NONE"):
        run([
        f'{Path(__file__).parent.absolute()}/obf.py',
        '-F',
        '-w',
        f"--key={key}",
        f'-n {file_name}',
        f'-i "{file_icon}"'
        ])
    else:
        run([
        f'{Path(__file__).parent.absolute()}/obf.py',
        '-F',
        '-w',
        f"--key={key}",
        f'-n {file_name}'
        ])
except Exception as e:
    print(e)

print("Build inished")
