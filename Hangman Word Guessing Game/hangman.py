import random

# Each stage visually adds one more part of the hangman, giving the player
# a clear indication of how close they are to running out of guesses.
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
    # Read the available words once and normalize them so comparison and display
    # stay consistent regardless of letter case or extra whitespace in the file.
    with open(filename, "r", encoding="utf-8") as file:
        return [word.strip().lower() for word in file if word.strip()]


def get_masked_word(word, guessed_letters):
    # Revealed letters stay visible, while every other character remains hidden.
    return " ".join(
        letter if letter in guessed_letters else "_"
        for letter in word
    )


def get_guess(guessed_letters):
    while True:
        guess = input("Guess a letter: ").strip().lower()

        # Keep asking until the player provides a single, unused alphabetic letter.
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter exactly one letter.")
        elif guess in guessed_letters:
            print("You've already guessed that letter.")
        else:
            return guess


def play_game():
    # Words are loaded from an external file so the same game can use a growing
    # or customized word list without changing the game logic.
    words = load_words("words.txt")
    if not words:
        print("Error: words.txt does not contain any words.")
        return

    word = random.choice(words)
    guessed_letters = set()
    wrong_guesses = 0

    print("Welcome to Hangman!")

    while wrong_guesses < MAX_WRONG_GUESSES:
        # Show the current drawing before each turn so the player can track progress.
        print(HANGMAN_STAGES[wrong_guesses])
        print("Word:", get_masked_word(word, guessed_letters))

        guess = get_guess(guessed_letters)
        guessed_letters.add(guess)

        if guess in word:
            print("Correct guess!")
        else:
            # A miss increases the stage counter and adds the next body part to the drawing.
            wrong_guesses += 1
            print("Wrong guess!")

        masked_word = get_masked_word(word, guessed_letters)

        if "_" not in masked_word:
            # Winning is determined from the fully revealed word, not the raw guesses.
            print(HANGMAN_STAGES[wrong_guesses])
            print("Word:", masked_word)
            print("Congratulations! You've guessed the word:", word)
            return

    # Reaching this point means every allowed wrong guess has been used.
    print(HANGMAN_STAGES[MAX_WRONG_GUESSES])
    print("Word:", get_masked_word(word, guessed_letters))
    print("Game Over! The word was:", word)


play_game()
