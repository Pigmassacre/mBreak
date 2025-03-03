# TODOs

## Fix collision bugs

- Balls sometimes get stuck in corners (block + block, block + wall).
- This was less common with just 3 columns of blocks.
- Maybe the ball collision system can be reworked entirely?

## Fix the fireworks effect in gameover.py

- The fireworks explode way before they reach their intended position near the middle / top middle of the screen.

## AI improvements

- The AI is too aggressive with using the laser at low energy levels.
- It should save up more energy before using the laser, especially at the start of the game when there are many blocks left.
- The AI should be more aggressive at targeting enemy blocks when firing the laser.

## Powerup spawn changes

- Powerups should spawn at 3 predetermined locations:
    - Right in the center of the field
    - In the top third
    - In the bottom third
- Powerups should only spawn at a location if there is no powerup at that location.

## Dummy TODO because Cursor fails to remove the last TODO for some reason

- Yup, AI is pretty cool though.