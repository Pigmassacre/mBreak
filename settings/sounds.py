import pygame
import os

"""
Sound manager that handles loading sound effects in both development and compiled environments.
"""

# Initialize the mixer
pygame.mixer.init(44100, -16, 2, 2048)

def get_sound(path):
    """Load a sound file with fallback for compiled version"""
    try:
        return pygame.mixer.Sound(path)
    except (FileNotFoundError, IOError):
        # In the compiled version, try without the 'res/' prefix
        try:
            return pygame.mixer.Sound(path.replace('res/', ''))
        except (FileNotFoundError, IOError):
            print(f"Warning: Could not load sound {path}")
            return None

def play_sound(sound):
    """Play a sound with the game's standard volume settings"""
    if sound is not None:
        channel = sound.play()
        if channel is not None:
            channel.set_volume(settings.SOUND_VOLUME)
        return channel
    return None

# Common sound effects
POWERUP_SOUNDS = [
    get_sound("res/sounds/powerup1.ogg"),
    get_sound("res/sounds/powerup2.ogg"),
    get_sound("res/sounds/powerup3.ogg"),
    get_sound("res/sounds/powerup4.ogg")
]

EXPLOSION_SOUNDS = [
    get_sound("res/sounds/explosion1.ogg"),
    get_sound("res/sounds/explosion2.ogg"),
    get_sound("res/sounds/explosion3.ogg"),
    get_sound("res/sounds/explosion4.ogg")
]

BALL_SOUND = get_sound("res/sounds/ball.ogg")
SELECT_SOUND = get_sound("res/sounds/select.ogg")
THUNDER_SOUND = get_sound("res/sounds/thunder.ogg")
FREEZING_SOUND = get_sound("res/sounds/freezing.ogg")
BURNING_SOUND = get_sound("res/sounds/burning.ogg")
EXPLOSION_SOUND = get_sound("res/sounds/explosion.ogg") 