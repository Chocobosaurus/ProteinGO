from cx_Freeze import setup, Executable
# Change these values accordingly
game_script = "proteinfly.py"  # Replace with your game's main script
base = None  # Set to "Win32GUI" if your game has a GUI
executables = [Executable(game_script, base=base)]
setup(name="proteinfly",
version="1.0",
description="PomLab game for Scientifica 2023 from Weijia",
executables=executables)
