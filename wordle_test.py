import unittest
import wordle


class TestGetFeedback(unittest.TestCase):
    def test_full_match(self):
        self.assertEqual(
            (
                wordle.Feedback.CORRECT,
                wordle.Feedback.CORRECT,
                wordle.Feedback.CORRECT,
                wordle.Feedback.CORRECT,
                wordle.Feedback.CORRECT,
            ),
            wordle.GetFeedback('tests', 'tests'),
        )

    def test_wrong_position(self):
        self.assertEqual(
            (
                wordle.Feedback.WRONG_POSITION,
                wordle.Feedback.CORRECT,
                wordle.Feedback.NOT_PRESENT,
                wordle.Feedback.NOT_PRESENT,
                wordle.Feedback.NOT_PRESENT,
            ),
            wordle.GetFeedback('ebfgh', 'abcde'),
        )

    def test_wrong_input(self):
        self.assertRaises(ValueError, wordle.GetFeedback, 'abc', 'ab')


class TestGetEntropy(unittest.TestCase):
    def test_low_entropy(self):
        self.assertEqual(0, wordle.GetEntropy({'x': 4, 'y': 0, 'z': 0}))

    def test_nonzero_entropy(self):
        self.assertAlmostEqual(
            -4 * 1.0 / 4 * -2, wordle.GetEntropy({'x': 1, 'y': 1, 'z': 1, 'w': 1})
        )


class TestEvaluateGuess(unittest.TestCase):
    def test_low_entropy(self):
        answers = set(['bbbbb', 'ccccc', 'ddddd'])
        self.assertEqual(0, wordle.EvaluateGuess('aaaaa', answers))

    def test_nonzero_entropy(self):
        answers = set(['bbbbb', 'ccccc'])
        entropy = wordle.EvaluateGuess('bbbbb', answers)
        self.assertAlmostEqual(-2.0 * 0.5 * -1, entropy)


class TestFindBestGuess(unittest.TestCase):
    def test_one_step_reveal(self):
        answers = ['car', 'far', 'war', 'tar']
        guesses = ['car', 'far', 'cfw']
        best_guess, score = wordle.FindBestGuess(guesses, answers)
        self.assertEqual('cfw', best_guess)
        self.assertAlmostEqual(-4.0 * 0.25 * -2, score)


class TestShouldKeep(unittest.TestCase):
    def test_not_in_word(self):
        self.assertTrue(wordle._ShouldKeep('test', not_in_word=set(['a', 'b', 'c'])))
        self.assertFalse(
            wordle._ShouldKeep('test', not_in_word=set(['t', 'a', 'b', 'c']))
        )

    def test_correct_letter(self):
        self.assertTrue(wordle._ShouldKeep('test', correct_letter=('tt', [0, 3])))
        self.assertFalse(wordle._ShouldKeep('test', correct_letter=('tt', [0, 1])))
        self.assertTrue(wordle._ShouldKeep('test', correct_letter=('', [])))

    def test_wrong_position(self):
        self.assertTrue(wordle._ShouldKeep('test', wrong_position={'t': [1, 2]}))
        self.assertFalse(wordle._ShouldKeep('test', wrong_position={'t': [0, 1, 2]}))
        self.assertFalse(wordle._ShouldKeep('test', wrong_position={'t': [0]}))


if __name__ == '__main__':
    unittest.main()
