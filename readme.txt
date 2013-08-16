README for mBreak

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
I am strongly considering open-sourcing it soon.

mBreak uses the animation library "Pyganim" made by Al Sweigart for animating the mBreak logo in the game.
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