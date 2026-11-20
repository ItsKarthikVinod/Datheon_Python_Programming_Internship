import random

HANGMAN_STAGES = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========
    """,
]

MAX_WRONG_GUESSES = 6


def load_words(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return [word.strip().lower() for word in file if word.strip()]


def get_masked_word(word, guessed_letters):
    return " ".join(
        letter if letter in guessed_letters else "_"
        for letter in word
    )


def get_guess(guessed_letters):
    while True:
        guess = input("Guess a letter: ").strip().lower()

        if len(guess) != 1 or not guess.isalpha():
            print("Please enter exactly one letter.")
        elif guess in guessed_letters:
            print("You've already guessed that letter.")
        else:
            return guess


def play_game():
    words = load_words("words.txt")
    if not words:
        print("Error: words.txt does not contain any words.")
        return

    word = random.choice(words)
    guessed_letters = set()
    wrong_guesses = 0

    print("Welcome to Hangman!")

    while wrong_guesses < MAX_WRONG_GUESSES:
        print(HANGMAN_STAGES[wrong_guesses])
        print("Word:", get_masked_word(word, guessed_letters))

        guess = get_guess(guessed_letters)
        guessed_letters.add(guess)

        if guess in word:
            print("Correct guess!")
        else:
            wrong_guesses += 1
            print("Wrong guess!")

        masked_word = get_masked_word(word, guessed_letters)

        if "_" not in masked_word:
            print(HANGMAN_STAGES[wrong_guesses])
            print("Word:", masked_word)
            print("Congratulations! You've guessed the word:", word)
            return

    print(HANGMAN_STAGES[MAX_WRONG_GUESSES])
    print("Word:", get_masked_word(word, guessed_letters))
    print("Game Over! The word was:", word)


play_game()
