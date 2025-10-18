import random
from pathlib import Path

# Load valid 5-letter words from a text file.
def load_words(path="WordList.txt"):
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    words = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().upper()
            if len(word) == 5 and word.isalpha():
                words.append(word)

    if not words:
        raise ValueError(f"File {path} does not contain valid words")
    return words

# Select a random word from the given list of words.
def choose_random_word(words):
    return random.choice(words)

