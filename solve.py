import argparse
from enum import Enum
import logging
import wordle
import wordmaster as wm
import wordle_words as ww

parser = argparse.ArgumentParser(description="""Mert's wordle solver implementation.""")
parser.add_argument(
    "action",
    type=str,
    choices=["init", "solve_for", "interactive"],
    help="Choose the mode of the solver.",
)
parser.add_argument(
    "--dictionary",
    type=str,
    choices=["wordle", "wordmaster"],
    default="wordle",
    help="Choose the dictionary.",
)

parser.add_argument("--secret", type=str, help="Word to guess in solve_for mode.")

logging.basicConfig(level=logging.INFO)

START_WORDS = {"wordle": "soare", "wordmaster": "tares"}

if __name__ == "__main__":
    args = parser.parse_args()
    if args.dictionary == "wordle":
        words = ww.words + ww.answers
        answers = ww.answers
    elif args.dictionary == "wordmaster":
        words = wm.words
        answers = wm.answers

    if args.action == "init":
        logging.info("Calculating the optimal starting word.")
        best_guess, score = wordle.FindBestGuess(words, answers)
        # wordmaster: tares
        # wordle: soare
        print("Best starting word is: {}".format(best_guess))
    elif args.action in ("solve_for", "interactive"):
        guess = START_WORDS[args.dictionary]
        score = 0.0
        step = 1
        feedback_str = ''
        while len(answers) > 1 and feedback_str != 'xxxxx':
            logging.info("Step {}:\tGuessing: {} ({:.3f})".format(step, guess, score))
            if args.action == "solve_for":
                if args.secret is None:
                    raise RuntimeError("--secret must be set in solve_for mode.")
                feedback = wordle.GetFeedback(guess, args.secret)
                feedback_str = wordle.PrintFeedback(feedback)
            else:
                feedback_str = input("Enter the feedback: ")
                feedback = wordle.ParseFeedback(feedback_str)
            logging.debug(feedback)
            words_size = len(words)
            answers_size = len(answers)
            words = wordle.PruneDictionary(words, guess, feedback)
            logging.debug(words)
            answers = set(answers).intersection(words)
            logging.info(
                "Guesses: {} ({}), Answers: {} ({}), Feedback: {}".format(
                    len(words),
                    words_size,
                    len(answers),
                    answers_size,
                    feedback_str
                )
            )
            guess, score = wordle.FindBestGuess(words, answers)
            step += 1
        if feedback_str == 'xxxxx':
            print('Answer found in last step.')
        else:
            print("Step {}: Answer is {}".format(step, answers.pop()))
    else:
        logging.info("The action is not implemented yet.")
