mBreak
======

Multiplayer Breakout 'clone' in Python. You know [Breakout](http://en.wikipedia.org/wiki/Breakout_(video_game\))? No? Perhaps you are more familiar with the name [Arkanoid](http://en.wikipedia.org/wiki/Arkanoid)? Well this game is part those games, and part [Pong](http://en.wikipedia.org/wiki/Pong) (You DO know what Pong is, do you?).

Still can't figure it out? I'll be more precise:<br/>
The game is like Pong, in that two opponents knock a ball around with their respective bats. Only in mBreak each player has their own ball. There are also <i>powerups</i>. Yeaah, powerups! Who doesn't like powerups? Man, I do like me some powerups.
Now, in Pong, the goal of the game is to make the ball touch your opponents wall (that's what it boils down to, anyway). Well, in mBreak the goal is for each player to destroy all of the opponents <b>blocks</b>. Much like in Breakout (or Arkanoid, whatever)!

So, to put it simply: Imagine Pong, but more like Breakout.

Coded for a summer course in Multimedia Programming with Python.

## Startup Instructions

[Pygame](http://pygame.org/) is needed, so download and install that.

This game requires [Pyganim](http://inventwithpython.com/pyganim/) library in order to function. This library is not included in this repo, so you need to download it yourself and place it in the libs/ folder.

All graphics are drawn by me (except for the lightning powerup, which is drawn by Anna Bjurb&auml;ck), so therefore they are included in the repo. However, none of the music required is made by me, so therefore you have to download those songs yourself. The required songs are, together with their licenses are:

You need to download any or all of the following mod-files (music files) yourself if you want the game to have any sort of music. You should, because these songs are awesome! Seriously. <i>Massive</i> cred to their authors.

These are:
* Title screen music: [sexxxy_bit_3!!!.xm](http://modarchive.org/index.php?request=view_by_moduleid&query=173084), made by Drozerix.

* Gameplay music: [stardstm.mod](http://modarchive.org/index.php?request=view_by_moduleid&query=59344), made by Jester.

* Post-game music: [october_chip.xm](http://modarchive.org/index.php?request=view_by_moduleid&query=173084), made by Drozerix. 

So download all of these, and place them under the res/music/ folder (if the folder doesn't exist, create it :P).

## Improvements

Investigate how to package the game. Ideally the user should be able to download a version of the game from Github.
* https://pyoxidizer.readthedocs.io/en/stable/
* http://nuitka.net/pages/overview.html

## Legal stuff

Both songs made by Drozerix are released under a [Public Domain](http://creativecommons.org/licenses/publicdomain/) license.<br/>
The song by Jester is released under a [Attribution Non-Commercial Share Alike](http://creativecommons.org/licenses/by-nc-sa/3.0/) license.

This project is released under the MIT license:

The MIT License (MIT)

Copyright &copy; 2013 Olof Karlsson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

So, simplified:
You may do whatever you want with this project. Fork it, edit it, release altered versions, whatever you want! Just make sure to keep the above license attached to whatever you decide to do with it.

However, if you do decide to do something with this project, I would love to know about it!

If you have any questions, drop me a mail at gulligaolle (at) gmail (dot) com! :)
