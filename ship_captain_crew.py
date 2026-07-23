#!/usr/bin/env python3
import argparse
import random
from typing import Dict, List, Tuple

REQUIRED_SEQUENCE = [("ship", 6), ("captain", 5), ("crew", 4)]
SCORE_KEEP_THRESHOLD = 4


def roll_dice(count: int) -> List[int]:
    return [random.randint(1, 6) for _ in range(count)]


def find_required_dice(dice: List[int], acquired: Dict[str, int]) -> Tuple[Dict[str, int], List[int]]:
    remaining = dice.copy()
    newly_acquired: Dict[str, int] = {}

    for name, value in REQUIRED_SEQUENCE:
        if name not in acquired and value in remaining:
            remaining.remove(value)
            newly_acquired[name] = value

    return newly_acquired, remaining


def keep_score_dice(dice: List[int]) -> Tuple[List[int], int]:
    kept = [die for die in dice if die >= SCORE_KEEP_THRESHOLD]
    reroll_count = len(dice) - len(kept)
    return kept, reroll_count


def play_round() -> int:
    acquired: Dict[str, int] = {}
    score_keep: List[int] = []
    dice_to_roll = 5

    for roll_number in range(1, 4):
        if len(acquired) < len(REQUIRED_SEQUENCE):
            dice = roll_dice(dice_to_roll)
            newly_acquired, remaining = find_required_dice(dice, acquired)
            acquired.update(newly_acquired)

            if len(acquired) == len(REQUIRED_SEQUENCE):
                score_keep = remaining
                dice_to_roll = len(score_keep)
            else:
                dice_to_roll = len(remaining)
        else:
            kept, reroll_count = keep_score_dice(score_keep)
            score_keep = kept + roll_dice(reroll_count)
            dice_to_roll = reroll_count

    if len(acquired) == len(REQUIRED_SEQUENCE):
        return sum(score_keep)

    return 0


def play_game(rounds: int = 12) -> Tuple[int, List[int]]:
    scores: List[int] = []

    for round_number in range(1, rounds + 1):
        round_score = play_round()
        scores.append(round_score)
        print(f"Round {round_number:2}: {round_score} points")

    total_score = sum(scores)
    print("\nFinal score after", rounds, "rounds:", total_score)
    print("Average score per round:", f"{total_score / rounds:.2f}")
    return total_score, scores


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play Ship, Captain, Crew (Cargo) with 5 dice and 3 tosses.")
    parser.add_argument("--rounds", type=int, default=12, help="Number of rounds to play.")
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducible games.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    print("Ship, Captain, Crew (Cargo)")
    print("Each round you get 3 tosses to roll a 6 (ship), 5 (captain), and 4 (crew). The remaining dice are your score.")
    print("If you fail to get ship/captain/crew, the round scores 0.")
    print("\nPlaying", args.rounds, "rounds...")

    play_game(args.rounds)


if __name__ == "__main__":
    main()
