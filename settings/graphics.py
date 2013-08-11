import os
import shutil

SHADOWS = True
PARTICLES = True
TRACES = True
BACKGROUND = True

def load():
	global SHADOWS
	global PARTICLES
	global TRACES
	global BACKGROUND

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
	finally:
		file.close()
			
def save():
	global SHADOWS
	global PARTICLES
	global TRACES
	global BACKGROUND

	# We use a temporary file to write to, so we don't corrupt our old file if the process fails.
	temp_file = open("settings.txt.tmp", "w")
	
	# Open and read the settings file.
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
		print("Error renaming and removing temporary file at end.")
	