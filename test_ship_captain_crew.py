import random
import unittest
from unittest.mock import patch

from ship_captain_crew import keep_score_dice, play_human_round, play_round


class TestShipCaptainCrew(unittest.TestCase):
    def test_keep_score_dice_keeps_high_values(self):
        dice = [6, 4, 3, 2]
        kept, reroll_count = keep_score_dice(dice)

        self.assertEqual(sorted(kept), [4, 6])
        self.assertEqual(reroll_count, 2)

    @patch("ship_captain_crew.random.randint")
    def test_play_round_scores_zero_without_full_set(self, mock_randint):
        mock_randint.side_effect = [6, 5, 1, 2, 3, 2, 5, 1, 2, 3, 2, 1, 2, 3, 4]
        score = play_round()
        self.assertEqual(score, 0)

    @patch("ship_captain_crew.random.randint")
    def test_play_round_scores_after_acquiring_required(self, mock_randint):
        # First roll gets Ship/Captain/Crew plus one extra high and one low die.
        # Then the low die is rerolled twice, ending with 6 and 3 for a 9-point round.
        mock_randint.side_effect = [6, 5, 4, 6, 1, 1, 3]
        score = play_round()
        self.assertEqual(score, 9)

    @patch("ship_captain_crew.prompt_keep_indices")
    @patch("ship_captain_crew.roll_dice")
    def test_human_turn_uses_all_three_tosses_after_required_set(self, mock_roll_dice, mock_prompt_keep_indices):
        mock_roll_dice.side_effect = [
            [4, 4, 6, 5, 6],
            [1, 2],
            [3, 4],
        ]
        mock_prompt_keep_indices.side_effect = [
            [0, 2, 3],
            [1, 2],
            [0, 1, 2],
        ]

        score = play_human_round("Player 1")
        self.assertEqual(score, 0)

    @patch("ship_captain_crew.prompt_keep_indices")
    @patch("ship_captain_crew.roll_dice")
    def test_human_turn_scores_remaining_dice_when_required_set_is_completed(self, mock_roll_dice, mock_prompt_keep_indices):
        mock_roll_dice.side_effect = [[6, 5, 4, 2, 3]]
        mock_prompt_keep_indices.side_effect = [[0, 1, 2]]

        score = play_human_round("Player 1")
        self.assertEqual(score, 5)

    @patch("builtins.input", return_value="y")
    @patch("ship_captain_crew.prompt_keep_indices")
    @patch("ship_captain_crew.roll_dice")
    def test_human_turn_prompts_to_keep_or_reroll_after_completed_set(self, mock_roll_dice, mock_prompt_keep_indices, mock_input):
        mock_roll_dice.side_effect = [[6, 5, 4, 2, 3]]
        mock_prompt_keep_indices.side_effect = [[0, 1, 2]]

        score = play_human_round("Player 1")
        self.assertEqual(score, 5)
        mock_input.assert_called()

    @patch("ship_captain_crew.prompt_keep_indices")
    @patch("ship_captain_crew.roll_dice")
    def test_human_turn_continues_after_empty_keep_selection(self, mock_roll_dice, mock_prompt_keep_indices):
        mock_roll_dice.side_effect = [[6, 2, 2, 5, 1], [1, 5, 2], [3, 4, 6]]
        mock_prompt_keep_indices.side_effect = [[], [], []]

        score = play_human_round("Player 1")
        self.assertEqual(score, 0)
        self.assertEqual(mock_roll_dice.call_count, 3)


if __name__ == "__main__":
    unittest.main()
