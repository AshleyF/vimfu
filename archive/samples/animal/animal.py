from node import *

animals = Node("Is it bigger than a breadbox?",
  Node("Does it primarily live in water?",
    Node("Whale"),
    Node("Is it larger than a car?",
      Node("Elephant"),
      Node("Mouse"))),
  Node("Is it known for being fast?",
    Node("Is it a mammal?",
      Node("Lion"),
      Node("Sparrow")),
    Node("Turtle")))

def guess(node):
  if node.yes is None and node.no is None:
    print(f"It's a {node.key}!")
    return
  response = input(f"{node.key} (y/n): ")
  if response == 'y':
    guess(node.yes)
  elif response == 'n':
    guess(node.no)
  else:
    print("Answer 'y'/'n'.")
    guess(node) # ask again

guess(animals)
