import subprocess

def install(name):
    subprocess.call(['pip', 'install', name])

try:
    import pyinstaller
except:
    install("pyinstaller")

subprocess.call(['pyinstaller', 'test.py','--onedir'])
