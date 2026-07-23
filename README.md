# dice_ship

This repository contains a Python implementation of the dice game "Ship, Captain, Crew" (also called "Cargo").

## How to play

- Roll 5 dice.
- You get up to 3 tosses per round.
- You must roll a 6 first (Ship), then a 5 (Captain), then a 4 (Crew).
- Only after you have Ship, Captain, and Crew can the remaining dice count as your score.
- If you fail to get the full set in 3 tosses, the round scores 0.
- The default game length is 12 rounds.

## Run the game

```bash
python3 ship_captain_crew.py
```

Use `--rounds` to change the number of rounds, and `--seed` to make results reproducible.

```bash
python3 ship_captain_crew.py --rounds 12 --seed 123
```
