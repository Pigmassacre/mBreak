README for mBreak

################################################################################

HELLO! Are you afraid you might not even be able to start the game? Well, fret not, this readme is here to help!

This game needs Python 2.7.4 and Pygame 1.9.1. If you are using Linux, like Ubuntu, then Python is probably
already installed on your computer. If it isn't or you are using some other operating system, like Windows, you
can download Python from here: http://python.org/download/

Pygame can be downloaded from here: http://pygame.org/download.shtml

Pygame needs a 32-bit version of Python, so make sure that you have a 32-bit version of Python installed (even
if you are on a 64-bit computer).

When everything is installed, to start the game on Windows you simply double-click mBreak.py in the mBreak folder.
On Linux, you must either be able to run python files as executable (I think...) or you can simply open a terminal-window
and navigate to the mBreak folder. When inside the folder, type "python mBreak.py" and press ENTER. This will
start the game.

After the game has started and the intro animation has been shown, click the screen or press the ENTER button to 
reach the main menu.

From the main menu, you can either start the game, go into an options menu or quit the game.

If you go into the options menu, you can either continue to a menu where you can turn special graphical effects on or off,
or go to a help menu which will explain certain details about the game. You can also go to an "About" menu where
you can read about where all the music comes from and stuff like that.

If you press the start button however, you are taken to a second screen where you will be required to pick a color
for both players. mBreak is multiplayer-ONLY, so if you do not have anyone to play against, well, I guess you can play against
yourself.

If you'd like, you can also choose the number of rounds that you want to play. The game will automatically decide
the winner if there is no point in playing any further rounds (say, if you play best out of 3, then after one player wins
2 times then that player ultimately wins!).

Once both players have chosen their colors, just press the START button in here to start the game.

You will be entered into the game, where a countdown will count down until the game begins. During the countdown
both players can move their paddles, but no balls will spawn.

After the countdown is over, one ball spawns per player. Your goal is then to break your opponents blocks while
you protect your own. You do this by moving your paddle up and down, just like in Pong!

When one player loses all his/her blocks, the round is over! If that was the last round, the winner is displayed
and you can there choose to either quit to the main menu, or go for a rematch.

If there are rounds left to be played, both players score will be displayed and you can either quit to the main menu
or start the next round.

During the game you can press the ESCAPE key to pause the game. In the pause menu you can either resume the game or quit to
the main menu. You must confirm your choice if you choose to quit, so you don't accidentally quit in the middle of a game.

There are several powerups available, but more info on those are in the help menu in the game!

Now, go have fun! I hope you enjoy mBreak! :)

################################################################################

mBreak is a multiplayer-breakout/pong style game coded during the summer of 2013 by me, Olof Karlsson AKA Pigmassacre.

mBreak was coded for the final assignment of the course "Multimediaprogrammering med Python" at the Stockholm University.

mBreak was coded on and tested with Python 2.7.4 on Ubuntu 13.04.

I get very good framerates (a consistent 60+ FPS) on my machine, an ASUS u46sv, using the above settings.
However, I cannot guarantee any good framerates on Windows. For some reason, using the exact same machine
my game runs at a meager ~30 FPS on Windows 7. By turning off the Backgrounds graphics settings (which can be done in-game or
in settings.txt) the framerate is improve dramatically, but still not as good as on Ubuntu 13.04.

I have no idea why this is. :/

mBreak is currently multiplayer only. You can, ofcourse, play by yourself, but there is no AI (or "bots") to play against.
I recommend a good friend with a good spirit of sportsmanship!

You can change the names of each player in the settings.txt file. The settings.txt file should be included in this release.
If it isn't, just start the game and the file will be created.

LICENSES AND LEGAL STUFF:
################################################################################

For now, the mBreak source is considered "All Rights Reserved".
I am strongly considering open-sourcing it soon, however.

Below are the things that I haven't made myself.

The font used is 8-BIT WONDER.TTF made by Joiro Hatagaya. The license and readme for this font is in the fonts/ folder.
The license states: "Currently all my fonts are freeware."

I think it's a really nice looking font. It lacks special characters though, so I have to make do without dots, commas and other
modern stuff. ;)

The title screen music is sexxxy_bit_3!!!.xm, made by Drozerix. I got it from
http://modarchive.org/index.php?request=view_by_moduleid&query=173084 which states that the song has a "Public Domain" license.
The public domain license can be read here: http://creativecommons.org/licenses/publicdomain/

The music that plays during gameplay is stardstm.mod, made by Jester. I got it from
http://modarchive.org/index.php?request=view_by_moduleid&query=59344 which states that the song has a "Attribution Non-Commercial
Share Alike" license, which can be read about here: http://creativecommons.org/licenses/by-nc-sa/3.0/

The post-game music is october_chip.xm, made by Drozerix. I got it from 
http://modarchive.org/index.php?request=view_by_moduleid&query=173084 which states that the song has a "Public Domain" license.
The public domain license can be read here: http://creativecommons.org/licenses/publicdomain/

IN NO WAY DO I CLAIM THAT I MADE, OWN OR IN ANY WAY CONTRIBUTED TO THESE SONGS. I simply think they are amazing, and I am 
VERY glad that they are released with such liberal licenses, allowing me to use them in mBreak.

Seriously, go check out more of Drozerix stuff, he has a ton of good chiptunes.

All sound effects except freezing.ogg made using www.bfxr.net.
The Bfxr website states: "You have full rights to all sounds made with bfxr, and are free to use them for commercial purposes."
The website is available at http://www.bfxr.net/

freezing.ogg is taken from http://www.soundjay.com/ice-sound-effect.html.
The soundjay license (which is available here: http://www.soundjay.com/tos.html) states:
"You are allowed to use the sounds free of charge and royalty free in your projects (such as films, videos, games, presentations, animations, stage plays, radio plays, audio books, apps) be it for commercial or non-commercial purposes."

mBreak uses the animation library "Pyganim" made by Al Sweigart for animating the mBreak logo in the game. The actual logo graphics
were made by myself, but the code used for animating it is all Pyganim.
The Pyganim source (which is not included in this game but can be seen at http://inventwithpython.com/pyganim/pyganim.py) states:

# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pyganim
# Released under a "Simplified BSD" license

I could not find a copy of the "Simplified BSD" on the Pyganim website, but the wikipedia article on BSD licenses has a copy.

The "Simplified BSD" license states:

############################# Simplified BSD ###################################

Copyright (c) 2011, Al Sweigart
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies, 
either expressed or implied, of the FreeBSD Project.

#### NOTE ###
Since this license wasn't actually in the pyganim source, I added in the year and owner myself. I took the year from the 
pyganim website (which states (c) 2011 Copyright Al Sweigart).