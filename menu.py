import pygame, sys
from pygame.locals import *
import pyganim

def setup_menu(titleY, titleX):
	textFont = pygame.font.Font("fonts/8-BIT WONDER.TTF", 18)

	startGameText = "Start"
	startGameMessage = textFont.render(startGameText, False, (255, 255, 255))
	startGameMessage.set_alpha(255)
	startGameMessageX = (screenWidth - textFont.size(startGameText)[0]) // 2
	startGameMessageY = titleY + 150
	
	quitGameText = "Quit"
	quitGameMessage = textFont.render(quitGameText, False, (255, 255, 255))
	quitGameMessage.set_alpha(255)
	quitGameMessageX = (screenWidth - textFont.size(quitGameText)[0]) // 2
	quitGameMessageY = titleY + 250

# Initiates the PyGame module.
pygame.init()
# Instantiates a PyGame Clock.
mainClock = pygame.time.Clock()

screenWidth = 640
screenHeight = 480
windowSurface = pygame.display.set_mode((screenWidth, screenHeight))

pygame.display.set_caption("mBreak")

title = pyganim.PygAnimation([("res/mBreakTitle_01.png", 1.00),
							("res/mBreakTitle_02.png", 0.075),
							("res/mBreakTitle_03.png", 0.075),
							("res/mBreakTitle_04.png", 0.075),
							("res/mBreakTitle_05.png", 0.075),
							("res/mBreakTitle_06.png", 0.075),
	 						("res/mBreakTitle_07.png", 0.075),
							("res/mBreakTitle_01.png", 1.00),
							("res/mBreakTitle_07.png", 0.075),
							("res/mBreakTitle_06.png", 0.075),
							("res/mBreakTitle_05.png", 0.075),
							("res/mBreakTitle_04.png", 0.075),
							("res/mBreakTitle_03.png", 0.075),
							("res/mBreakTitle_02.png", 0.075)])

title.play()

# Set the mBreak title logo so it displays in the middle of the screen.
# title.getMaxSize()[0] gets width, [1] gets height.
titleX = (screenWidth - title.getMaxSize()[0]) // 2
titleY = ((screenHeight - title.getMaxSize()[1]) // 2) - 175

# Sets the blink rate of the message.
titleMessageBlinkRate = 750

# Sets the background color to black.							
backgroundColor = (0, 0, 0)

def blinkMessage(surface, timePassed, blinkRate):
	"""
	Switches the target surface alpha value between 255 and 0 every blinkRate.
	The surface spends 2/3s of the time with alpha value 0 as with 255.
	"""
	if timePassed > blinkRate:
		if surface.get_alpha() == 255:
			surface.set_alpha(0)
			return blinkRate // 3
		else:
			surface.set_alpha(255)
			return 0
	else:
		return timePassed
			
# Keeps track of how much time has passed.
timePassed = 0

while True:
	windowSurface.fill(backgroundColor)
	
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			# If the ESCAPE key is pressed or the window is closed, the game is shut down.
			pygame.quit()
			sys.exit()
	
	timePassed += mainClock.get_time()
	
	# Blinks the title message. Sets the timePassed value to either blinkRate // 3 or 0.
	timePassed = blinkMessage(titleMessage, timePassed, titleMessageBlinkRate)
	
	# Pyganim blits object to the given argument, pygame blits the given argument to object...
	title.blit(windowSurface, (titleX, titleY))
	windowSurface.blit(startGameMessage, (startGameMessageX, startGameMessageY))
	windowSurface.blit(quitGameMessage, (quitGameMessageX, quitGameMessageY))
	
	windowSurface.blit(titleFont.render(str(timePassed), False, (255, 255, 255)), (25, 25))
	
	pygame.display.update()
	
	# Sets the maximum FPS to 60.
	mainClock.tick(60)

