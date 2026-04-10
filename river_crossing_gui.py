import tkinter as tk
from tkinter import messagebox


class RiverCrossingGame:
    def __init__(self):
        self.left = {"Farmer", "Wolf", "Goat", "Cabbage"}
        self.right = set()
        self.farmer_side = "left"

    def is_valid(self):
        # Check left bank
        if "Farmer" not in self.left:
            if "Wolf" in self.left and "Goat" in self.left:
                return False, "The wolf ate the goat on the LEFT bank!"
            if "Goat" in self.left and "Cabbage" in self.left:
                return False, "The goat ate the cabbage on the LEFT bank!"

        # Check right bank
        if "Farmer" not in self.right:
            if "Wolf" in self.right and "Goat" in self.right:
                return False, "The wolf ate the goat on the RIGHT bank!"
            if "Goat" in self.right and "Cabbage" in self.right:
                return False, "The goat ate the cabbage on the RIGHT bank!"

        return True, ""

    def is_won(self):
        return self.right == {"Farmer", "Wolf", "Goat", "Cabbage"}

    def move(self, item):
        current_bank = self.left if self.farmer_side == "left" else self.right
        other_bank = self.right if self.farmer_side == "left" else self.left

        if item != "None" and item not in current_bank:
            return False, f"{item} is not on the same side as the farmer."

        # Move farmer
        current_bank.remove("Farmer")
        other_bank.add("Farmer")

        # Move chosen item if any
        if item != "None":
            current_bank.remove(item)
            other_bank.add(item)

        # Update farmer side
        self.farmer_side = "right" if self.farmer_side == "left" else "left"

        return True, f"Farmer moved with {item}" if item != "None" else "Farmer moved alone"

    def get_possible_moves(self):
        current_bank = self.left if self.farmer_side == "left" else self.right
        items = [item for item in current_bank if item != "Farmer"]
        return ["None"] + sorted(items)

    def reset(self):
        self.left = {"Farmer", "Wolf", "Goat", "Cabbage"}
        self.right = set()
        self.farmer_side = "left"


class RiverCrossingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wolf-Goat-Cabbage River Crossing Puzzle")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.game = RiverCrossingGame()

        title = tk.Label(
            root,
            text="Wolf - Goat - Cabbage River Crossing Puzzle",
            font=("Arial", 18, "bold"),
            pady=10
        )
        title.pack()

        rules = tk.Label(
            root,
            text="Rules: Boat carries Farmer + ONE item | Wolf cannot stay with Goat | Goat cannot stay with Cabbage",
            font=("Arial", 10),
            wraplength=650,
            justify="center"
        )
        rules.pack(pady=5)

        self.state_frame = tk.Frame(root)
        self.state_frame.pack(pady=20)

        self.left_label_title = tk.Label(self.state_frame, text="Left Bank", font=("Arial", 14, "bold"))
        self.left_label_title.grid(row=0, column=0, padx=50)

        self.river_label = tk.Label(self.state_frame, text="~~~~~ RIVER ~~~~~", font=("Arial", 14, "bold"), fg="blue")
        self.river_label.grid(row=0, column=1, padx=20)

        self.right_label_title = tk.Label(self.state_frame, text="Right Bank", font=("Arial", 14, "bold"))
        self.right_label_title.grid(row=0, column=2, padx=50)

        self.left_bank_label = tk.Label(self.state_frame, text="", font=("Arial", 12), width=20, height=10, relief="solid")
        self.left_bank_label.grid(row=1, column=0, padx=20, pady=10)

        self.boat_label = tk.Label(self.state_frame, text="", font=("Arial", 12, "bold"))
        self.boat_label.grid(row=1, column=1, padx=20)

        self.right_bank_label = tk.Label(self.state_frame, text="", font=("Arial", 12), width=20, height=10, relief="solid")
        self.right_bank_label.grid(row=1, column=2, padx=20, pady=10)

        self.status_label = tk.Label(root, text="Game started!", font=("Arial", 12), fg="green")
        self.status_label.pack(pady=10)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=20)

        self.move_buttons = {}

        for item in ["None", "Wolf", "Goat", "Cabbage"]:
            text = "Farmer Alone" if item == "None" else f"Take {item}"
            btn = tk.Button(
                self.button_frame,
                text=text,
                font=("Arial", 11),
                width=15,
                command=lambda i=item: self.handle_move(i)
            )
            btn.pack(side="left", padx=10)
            self.move_buttons[item] = btn

        self.restart_button = tk.Button(
            root,
            text="Restart Game",
            font=("Arial", 11, "bold"),
            bg="lightgray",
            command=self.restart_game
        )
        self.restart_button.pack(pady=10)

        self.update_display()

    def update_display(self):
        left_text = "\n".join(sorted(self.game.left)) if self.game.left else "None"
        right_text = "\n".join(sorted(self.game.right)) if self.game.right else "None"

        self.left_bank_label.config(text=left_text)
        self.right_bank_label.config(text=right_text)

        self.boat_label.config(text=f"Boat is on\n{self.game.farmer_side.upper()} side")

        possible_moves = self.game.get_possible_moves()
        for item, btn in self.move_buttons.items():
            if item in possible_moves:
                btn.config(state="normal")
            else:
                btn.config(state="disabled")

    def handle_move(self, item):
        success, msg = self.game.move(item)

        if not success:
            self.status_label.config(text=msg, fg="red")
            return

        valid, reason = self.game.is_valid()
        self.update_display()

        if not valid:
            self.status_label.config(text=reason, fg="red")
            messagebox.showerror("Game Over", reason)
            self.disable_all_buttons()
            return

        if self.game.is_won():
            self.status_label.config(text="Congratulations! You solved the puzzle.", fg="green")
            messagebox.showinfo("You Won!", "Congratulations! You solved the puzzle.")
            self.disable_all_buttons()
            return

        self.status_label.config(text=msg, fg="blue")

    def disable_all_buttons(self):
        for btn in self.move_buttons.values():
            btn.config(state="disabled")

    def restart_game(self):
        self.game.reset()
        self.status_label.config(text="Game restarted!", fg="green")
        self.update_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = RiverCrossingGUI(root)
    root.mainloop()