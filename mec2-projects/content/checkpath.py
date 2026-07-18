import os

# Common default locations for ngrok configuration files on Windows
possible_paths = [
    os.path.expandvars(r"%USERPROFILE%\.config\ngrok\ngrok.yml"),
    os.path.expandvars(r"%LOCALAPPDATA%\ngrok\ngrok.yml"),
    os.path.expandvars(r"%USERPROFILE%\.ngrok2\ngrok.yml")
]

found = False
for path in possible_paths:
    if os.path.exists(path):
        found = True
        print(f"Found config at: {path}")
        try:
            # Overwrite the file to reset it to a clean slate
            with open(path, 'w') as f:
                f.write("version: \"2\"\n")
            print("Successfully reset ngrok.yml to factory defaults!")
        except Exception as e:
            print(f"Could not reset file: {e}")
        break

if not found:
    print("Could not find ngrok.yml in default locations. Try running your main script with an ephemeral port.")