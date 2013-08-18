import os
import shutil

"""

Contains the graphical options on the game

"""

SHADOWS = True
PARTICLES = True
TRACES = True
BACKGROUND = True
FULLSCREEN = False
MAX_FPS = 60

def load():
	# Tries to load the graphics options from settings.txt.
	global SHADOWS
	global PARTICLES
	global TRACES
	global BACKGROUND
	global FULLSCREEN
	global MAX_FPS

	# We have to make sure we always call settings.load() before graphics.load(), since settings.load()
	# takes care of creating the .txt file. mBreak.py does it in this way.

	# Open and read the settings file line by line.
	file = open("settings.txt", "r")
	try:
		for line in file:
			if "shadows" in line:
				SHADOWS = bool(int(line.strip("shadows").strip()))
			elif "particles" in line:
				PARTICLES = bool(int(line.strip("particles").strip()))
			elif "traces" in line:
				TRACES = bool(int(line.strip("traces").strip()))
			elif "background" in line:
				BACKGROUND = bool(int(line.strip("background").strip()))
			elif "fullscreen" in line:
				FULLSCREEN = bool(int(line.strip("fullscreen").strip()))
			elif "maxfps" in line:
				MAX_FPS = int(line.strip("maxfps").strip())
				print(MAX_FPS)
	finally:
		file.close()
			
def save():
	# Tries to save the graphics options to settings.txt.
	global SHADOWS
	global PARTICLES
	global TRACES
	global BACKGROUND
	global FULLSCREEN

	# We use a temporary file to write to, so we don't corrupt our old file if the process fails.
	temp_file = open("settings.txt.tmp", "w")
	
	# Open and read the settings file line by line.
	file = open("settings.txt", "r+")
	try:
		for line in file:
			if "shadows" in line:
				temp_file.write(line.replace(line.strip("shadows").strip(), str(int(SHADOWS))))
			elif "particles" in line:
				temp_file.write(line.replace(line.strip("particles").strip(), str(int(PARTICLES))))
			elif "traces" in line:
				temp_file.write(line.replace(line.strip("traces").strip(), str(int(TRACES))))
			elif "background" in line:
				temp_file.write(line.replace(line.strip("background").strip(), str(int(BACKGROUND))))
			elif "fullscreen" in line:
				temp_file.write(line.replace(line.strip("fullscreen").strip(), str(int(FULLSCREEN))))
			elif "maxfps" in line:
				temp_file.write(line.replace(line.strip("maxfps").strip(), str(int(MAX_FPS))))
			else:
				temp_file.write(line)
	finally:		
		# We must remember to close both files since we're done.
		temp_file.close()
		file.close()
	
	# We're done, so we rename the temp file.
	try:
		shutil.copy("settings.txt", "settings.txt.backup")
		os.remove("settings.txt")
		os.rename("settings.txt.tmp", "settings.txt")
		os.remove("settings.txt.backup")
	except OSError:
		print("Error renaming and removing temporary file at end of the procedure.")
	