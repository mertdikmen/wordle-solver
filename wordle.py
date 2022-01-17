from collections import Counter, defaultdict
from enum import Enum
import logging
import math
from typing import Any, Iterable
from multiprocessing import Pool

class Feedback(Enum):
    CORRECT = 1
    WRONG_POSITION = 2
    NOT_PRESENT = 3


_FEEDBACK_LETTERS = {
    Feedback.CORRECT: "x",
    Feedback.WRONG_POSITION: "?",
    Feedback.NOT_PRESENT: ".",
}

_FEEDBACK_LETTERS_INV = {
    "x": Feedback.CORRECT,
    "?": Feedback.WRONG_POSITION,
    ".": Feedback.NOT_PRESENT,
}


def GetFeedback(guess: str, word: str) -> tuple[Feedback]:
    if len(guess) != len(word):
        raise ValueError("{} and {} are not the same length".format(guess, word))

    feedback = []
    letters = set(word)
    for i, l in enumerate(guess):
        if l == word[i]:
            feedback.append(Feedback.CORRECT)
        elif l in letters:
            feedback.append(Feedback.WRONG_POSITION)
        else:
            feedback.append(Feedback.NOT_PRESENT)
    return tuple(feedback)


def GetEntropy(outcome_map: dict[Any, int]) -> float:
    entropy = 0
    space_size = sum(outcome_map.values())
    ent = lambda x: 0 if x == 0 else x / space_size * math.log2(x / space_size)
    return sum([-ent(e) for e in outcome_map.values()])


def EvaluateGuess(guess: str, answers: set[str]) -> float:
    counts = Counter([GetFeedback(guess, a) for a in answers])
    return GetEntropy(counts)


def FindBestGuess(guesses: Iterable[str], answers: Iterable[str]) -> tuple[str, float]:
    with Pool(processes=multiprocessing.cpu_count()) as p:
        results = p.starmap(EvaluateGuess, ([guess, answers] for guess in guesses))
    max_score = -1
    best_guess = ""
    for i, (guess, score) in enumerate(zip(guesses, results)):
        if score > max_score:
            max_score = score
            best_guess = guess
            logging.debug("Best guess updated: {} ({:3f})".format(best_guess, score))
        if i % 100 == 0:
            logging.debug("{}/{}".format(i, len(guesses)))
    return (best_guess, max_score)


def _ShouldKeep(
    word,
    not_in_word: set[str] = set(),
    correct_letter: tuple[str, Iterable[int]] = ("", []),
    wrong_position: dict[str, Iterable[int]] = {},
):
    if len(correct_letter[0]) != 0 and (
        correct_letter[0] != "".join([word[i] for i in correct_letter[1]])
    ):
        return False
    if not not_in_word.isdisjoint(word):
        return False
    for letter, wrong_indices in wrong_position.items():
        subword = "".join([word[i] for i in wrong_indices])
        if letter in subword:
            return False
        if letter not in word:
            return False
    return True


def PruneDictionary(
    words: Iterable[str], guess: str, feedbacks: tuple[Feedback]
) -> Iterable[str]:
    not_in_word = set()
    correct_letter = ("", [])
    wrong_position = defaultdict(set)
    for i, feedback in enumerate(feedbacks):
        if feedback == Feedback.NOT_PRESENT:
            not_in_word.add(guess[i])
        elif feedback == Feedback.CORRECT:
            correct_letter = (correct_letter[0] + guess[i], correct_letter[1] + [i])
        else:  # feedback == Feedback.WRONG_POSITION
            wrong_position[guess[i]].add(i)

    return [
        w for w in words if _ShouldKeep(w, not_in_word, correct_letter, wrong_position)
    ]


def PrintFeedback(feedbacks: tuple[Feedback]) -> str:
    return "".join([_FEEDBACK_LETTERS[f] for f in feedbacks])


def ParseFeedback(feedback_str: str) -> tuple[Feedback]:
    return tuple([_FEEDBACK_LETTERS_INV[l] for l in feedback_str])
