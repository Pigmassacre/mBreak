# TODOs

## Improve the block health rendering

- Currently the darkness of each block only changes when the block reaches half health. I think it would be more clear if the health of each block was directly represented by the tint of the block graphics.

## Fix the fireworks effect in gameover.py

- The fireworks explode way before they reach their intended position near the middle / top middle of the screen.

## AI improvements

- The AI is too aggressive with using the laser at low energy levels.
- It should save up more energy before using the laser, especially at the start of the game when there are many blocks left.
- The AI should be more aggressive at targeting enemy blocks when firing the laser.

## Block changes

- Each player currently has 3 columns of blocks. This should be changed to 4 columns of blocks.
- Each players paddle should be moved one blocks width closer to the center to accomodate for this change.
- The last two columns of blocks for each player (the columns farthest away from the center) should have twice as much health.
- Blocks that have more health than the default health should show that visually by being applying a shiny tint to them.

## Powerup spawn changes

- Powerups should spawn at 3 predetermined locations:
    - Right in the center of the field
    - In the top third
    - In the bottom third
- Powerups should only spawn at a location if there is no powerup at that location.

## Dummy TODO because Cursor fails to remove the last TODO for some reason

- Yup, AI is pretty cool though.