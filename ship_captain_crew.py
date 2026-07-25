#!/usr/bin/env python3
import argparse
import random
from collections import Counter
from typing import Dict, List, Optional, Tuple

REQUIRED_SEQUENCE = [("ship", 6), ("captain", 5), ("crew", 4)]
REQUIRED_VALUES = {value for _, value in REQUIRED_SEQUENCE}
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


def prompt_keep_indices(dice: List[int]) -> List[int]:
    print("Dice:", " ".join(f"[{index + 1}:{die}]" for index, die in enumerate(dice)))
    raw = input("Enter dice positions to keep (1-based, comma or space separated; press enter to keep none and continue): ").strip()

    if not raw:
        return []

    normalized = raw.replace(",", " ")
    positions: List[int] = []
    for token in normalized.split():
        try:
            position = int(token)
        except ValueError:
            raise ValueError("Keep positions must be whole numbers.")

        if position < 1 or position > len(dice):
            raise ValueError("Keep positions must be between 1 and the number of dice in the roll.")

        positions.append(position - 1)

    return sorted(set(positions))


def next_required_value(acquired: Dict[str, int]) -> Optional[int]:
    for name, value in REQUIRED_SEQUENCE:
        if name not in acquired:
            return value
    return None


def validate_keep_positions(current_dice: List[int], acquired: Dict[str, int], keep_positions: List[int]) -> List[int]:
    if not keep_positions:
        return []

    required_value = next_required_value(acquired)
    if required_value is None:
        return keep_positions

    selected_values = [current_dice[index] for index in keep_positions]
    if required_value not in selected_values:
        raise ValueError(f"You must keep the next required die: {required_value}.")

    return keep_positions


def score_after_required(acquired: Dict[str, int], kept_dice: List[int]) -> int:
    if len(acquired) < len(REQUIRED_SEQUENCE):
        return 0

    required_used = set(acquired.values())
    return sum(die for die in kept_dice if die not in required_used)


def play_round() -> int:
    acquired: Dict[str, int] = {}
    dice_to_roll = 5

    for _ in range(3):
        dice = roll_dice(dice_to_roll)
        newly_acquired, remaining = find_required_dice(dice, acquired)
        acquired.update(newly_acquired)

        if len(acquired) == len(REQUIRED_SEQUENCE):
            return sum(remaining)

        dice_to_roll = len(remaining)

    return 0


def prompt_keep_or_reroll(player_name: str, cargo_score: int, remaining_rolls: int) -> bool:
    if remaining_rolls <= 0:
        return False

    prompt = (
        f"{player_name}, you have completed Ship, Captain, Crew. "
        f"Current cargo score is {cargo_score}. "
        f"Keep this score and end the turn? [y/n]: "
    )
    while True:
        raw = input(prompt).strip().lower()
        if raw in {"", "y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please enter 'y' to keep the current score or 'n' to reroll the cargo dice.")


def play_human_round(player_name: str) -> int:
    acquired: Dict[str, int] = {}
    held_dice: List[int] = []
    cargo_dice: List[int] = []

    print(f"\n{player_name}'s turn")
    print("Rule: keep a 6 first, then a 5, then a 4 to complete Ship, Captain, Crew.")

    for toss in range(1, 4):
        if len(acquired) == len(REQUIRED_SEQUENCE):
            cargo_score = sum(cargo_dice)
            if toss == 3:
                print(f"{player_name} reached Ship, Captain, Crew. Cargo score: {cargo_score}")
                return cargo_score

            keep_current_score = prompt_keep_or_reroll(player_name, cargo_score, 4 - toss)
            if keep_current_score:
                print(f"{player_name} kept the current cargo score: {cargo_score}")
                return cargo_score

            print(f"{player_name} chose to reroll the cargo dice.")
            current_dice = roll_dice(len(cargo_dice) or 5)
            print(f"Toss {toss}: {current_dice}")
            cargo_dice = current_dice
            continue

        roll_count = len(cargo_dice) if cargo_dice else 5
        if roll_count <= 0:
            print("No dice remain to roll. Ending the turn.")
            break

        print(f"\nHeld dice: {held_dice}")
        print(f"Rolling {roll_count} new dice...")
        current_dice = roll_dice(roll_count)
        print(f"Toss {toss}: {current_dice}")

        try:
            keep_positions = prompt_keep_indices(current_dice)
            keep_positions = validate_keep_positions(current_dice, acquired, keep_positions)
        except ValueError as exc:
            print(f"Invalid input: {exc}")
            print("Please try again.")
            return 0

        if not keep_positions:
            print(f"{player_name} kept no dice this roll and will continue.")
            cargo_dice = current_dice
            continue

        selected_values = [current_dice[index] for index in keep_positions]
        held_dice.extend(selected_values)

        for name, value in REQUIRED_SEQUENCE:
            if name not in acquired and value in selected_values:
                acquired[name] = value

        remaining_dice = [die for index, die in enumerate(current_dice) if index not in keep_positions]
        cargo_dice = remaining_dice

        if len(acquired) == len(REQUIRED_SEQUENCE):
            cargo_score = sum(cargo_dice)
            print(f"{player_name} reached Ship, Captain, Crew. Cargo score: {cargo_score}")
            if toss < 3:
                keep_current_score = prompt_keep_or_reroll(player_name, cargo_score, 4 - toss)
                if keep_current_score:
                    print(f"{player_name} kept the current cargo score: {cargo_score}")
                    return cargo_score
                print(f"{player_name} chose to reroll the cargo dice.")
                continue
            return cargo_score

        missing = [name for name, _ in REQUIRED_SEQUENCE if name not in acquired]
        print(f"{player_name} still needs: {', '.join(missing)}")

    if len(acquired) != len(REQUIRED_SEQUENCE):
        print(f"{player_name} did not complete the set and gets 0 this round.")
        return 0

    return sum(cargo_dice)


def play_game(rounds: int = 10, player_names: Optional[List[str]] = None) -> Dict[str, int]:
    if player_names is None:
        player_names = ["Player 1"]

    total_scores: Dict[str, int] = {name: 0 for name in player_names}
    for round_number in range(1, rounds + 1):
        print(f"\n=== Round {round_number} ===")
        for player_name in player_names:
            round_score = play_human_round(player_name)
            total_scores[player_name] += round_score
            print(f"{player_name} now has {total_scores[player_name]} total points.")

    print("\nFinal scores:")
    for player_name, score in total_scores.items():
        print(f"- {player_name}: {score}")

    return total_scores


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play Ship, Captain, Crew (Cargo) with 5 dice and 3 tosses.")
    parser.add_argument("--rounds", type=int, default=12, help="Number of rounds to play.")
    parser.add_argument("--players", type=int, default=None, help="Number of players in the game.")
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducible games.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    if args.players is None:
        while True:
            try:
                raw_players = input("How many players? ").strip()
                args.players = int(raw_players)
                if args.players > 0:
                    break
                print("Please enter a positive whole number of players.")
            except ValueError:
                print("Please enter a whole number for the player count.")

    print("Ship, Captain, Crew (Cargo)")
    print("Each round you get 3 tosses to roll a 6 (ship), 5 (captain), and 4 (crew).")
    print("After you have all three, the remaining dice become your score.")
    print("Choose which dice to keep by entering their 1-based positions after each toss.")

    player_names = [f"Player {index}" for index in range(1, args.players + 1)]
    play_game(args.rounds, player_names)


if __name__ == "__main__":
    main()
