# river_crossing.py

class RiverCrossingGame:
    def __init__(self):
        self.left = {"Farmer", "Wolf", "Goat", "Cabbage"}
        self.right = set()
        self.farmer_side = "left"

    def display_state(self):
        print("\n" + "=" * 50)
        print(f"Left Bank : {', '.join(sorted(self.left)) if self.left else 'None'}")
        print(f"Right Bank: {', '.join(sorted(self.right)) if self.right else 'None'}")
        print(f"Farmer is on the {self.farmer_side.upper()} bank")
        print("=" * 50)

    def is_valid(self):
        # Check left bank
        if "Farmer" not in self.left:
            if "Wolf" in self.left and "Goat" in self.left:
                print("The wolf ate the goat on the LEFT bank!")
                return False
            if "Goat" in self.left and "Cabbage" in self.left:
                print("The goat ate the cabbage on the LEFT bank!")
                return False

        # Check right bank
        if "Farmer" not in self.right:
            if "Wolf" in self.right and "Goat" in self.right:
                print("The wolf ate the goat on the RIGHT bank!")
                return False
            if "Goat" in self.right and "Cabbage" in self.right:
                print("The goat ate the cabbage on the RIGHT bank!")
                return False

        return True

    def is_won(self):
        return self.right == {"Farmer", "Wolf", "Goat", "Cabbage"}

    def move(self, item):
        current_bank = self.left if self.farmer_side == "left" else self.right
        other_bank = self.right if self.farmer_side == "left" else self.left

        if item != "None" and item not in current_bank:
            print(f"{item} is not on the same side as the farmer.")
            return

        # Move farmer
        current_bank.remove("Farmer")
        other_bank.add("Farmer")

        # Move chosen item if any
        if item != "None":
            current_bank.remove(item)
            other_bank.add(item)

        # Update farmer side
        self.farmer_side = "right" if self.farmer_side == "left" else "left"

    def get_possible_moves(self):
        current_bank = self.left if self.farmer_side == "left" else self.right
        items = [item for item in current_bank if item != "Farmer"]
        return ["None"] + sorted(items)

    def play(self):
        print("Welcome to the Wolf-Goat-Cabbage River Crossing Puzzle!")
        print("Goal: Take all items safely across the river.")
        print("Rules:")
        print("- Boat carries Farmer + ONE item")
        print("- Wolf cannot be left alone with Goat")
        print("- Goat cannot be left alone with Cabbage")

        while True:
            self.display_state()

            if self.is_won():
                print("\nCongratulations! You solved the puzzle.")
                break

            moves = self.get_possible_moves()
            print("\nPossible moves:")
            for i, move in enumerate(moves, 1):
                print(f"{i}. {move}")

            try:
                choice = int(input("Choose a move number: "))
                if choice < 1 or choice > len(moves):
                    print("Invalid choice. Try again.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue

            selected_move = moves[choice - 1]
            self.move(selected_move)

            if not self.is_valid():
                self.display_state()
                print("\nGame Over!")
                break


if __name__ == "__main__":
    game = RiverCrossingGame()
    game.play()