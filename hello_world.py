#!/usr/bin/env python3
"""
My First Python Program - Hello World
This is a simple program to demonstrate basic Python syntax.
"""


def main():
    """Main function that runs when the program starts."""
    print("Hello, World!")
    print("Welcome to your first Python program!")

    # Get user input
    name = input("What's your name? ")
    print(f"Nice to meet you, {name}!")

    # Simple calculation
    age = int(input("How old are you? "))
    print(f"In 10 years, you'll be {age + 10} years old!")


if __name__ == "__main__":
    main()
