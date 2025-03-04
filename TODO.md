# TODOs

## Collision fixes

The revamped ball collision handling is way better, but it has some insane bugs:

- Balls can sometimes get into a weird state where they stick to a vertical wall, continuously reporting collisions and spawning particles but not moving away from the wall.
- Very rarely if a ball collides with a corner of the stage it can get stuck in a collision loop and slowly work its way out of the arena.

## AI fixes

- The AI sometimes misses incredibly obvious balls - often not moving the paddle at all.
- The AI doesnt get out of the way of balls that are behind it (for player 1 left of the paddle, for player 2 right of the paddle).

## Dummy TODO because Cursor fails to remove the last TODO for some reason

- Yup, AI is pretty cool though.