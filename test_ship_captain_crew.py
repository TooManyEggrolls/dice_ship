import random
import unittest
from unittest.mock import patch

from ship_captain_crew import keep_score_dice, play_round


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


if __name__ == "__main__":
    unittest.main()
