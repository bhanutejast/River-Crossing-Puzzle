import tkinter as tk
from tkinter import messagebox


class RiverCrossingGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.left = {"Farmer", "Wolf", "Goat", "Cabbage"}
        self.right = set()
        self.farmer_side = "left"
        self.history = []

    def is_valid(self):
        if "Farmer" not in self.left:
            if "Wolf" in self.left and "Goat" in self.left:
                return False, "The wolf ate the goat on the LEFT bank!"
            if "Goat" in self.left and "Cabbage" in self.left:
                return False, "The goat ate the cabbage on the LEFT bank!"

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

        current_bank.remove("Farmer")
        other_bank.add("Farmer")

        if item != "None":
            current_bank.remove(item)
            other_bank.add(item)
            self.history.append(f"Farmer takes {item}")
        else:
            self.history.append("Farmer goes alone")

        self.farmer_side = "right" if self.farmer_side == "left" else "left"
        return True, self.history[-1]

    def get_possible_moves(self):
        current_bank = self.left if self.farmer_side == "left" else self.right
        items = [item for item in current_bank if item != "Farmer"]
        return ["None"] + sorted(items)


class RiverCrossingDeluxeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("River Crossing Puzzle - Deluxe Edition")
        self.root.geometry("1100x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        self.game = RiverCrossingGame()
        self.is_animating = False

        self.item_icons = {
            "Farmer": "👨‍🌾",
            "Wolf": "🐺",
            "Goat": "🐐",
            "Cabbage": "🥬"
        }

        self.item_colors = {
            "Farmer": "#facc15",
            "Wolf": "#cbd5e1",
            "Goat": "#fde68a",
            "Cabbage": "#86efac"
        }

        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#1e293b", height=80)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="🌊 River Crossing Puzzle - Deluxe Edition",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg="#1e293b"
        )
        title.pack(pady=18)

        subtitle = tk.Label(
            self.root,
            text="Move everyone safely across the river without breaking the rules.",
            font=("Segoe UI", 12),
            fg="#cbd5e1",
            bg="#0f172a"
        )
        subtitle.pack(pady=8)

        main = tk.Frame(self.root, bg="#0f172a")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        self.left_panel = tk.Frame(main, bg="#166534", width=230, height=450, bd=3, relief="ridge")
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        center_panel = tk.Frame(main, bg="#0f172a")
        center_panel.grid(row=0, column=1, padx=10, pady=10)

        self.right_panel = tk.Frame(main, bg="#166534", width=230, height=450, bd=3, relief="ridge")
        self.right_panel.grid(row=0, column=2, padx=10, pady=10, sticky="ns")

        side_panel = tk.Frame(main, bg="#1e293b", width=280, height=450, bd=3, relief="ridge")
        side_panel.grid(row=0, column=3, padx=10, pady=10, sticky="ns")

        self.left_panel.grid_propagate(False)
        self.right_panel.grid_propagate(False)
        side_panel.grid_propagate(False)

        tk.Label(
            self.left_panel, text="LEFT BANK", font=("Segoe UI", 16, "bold"),
            fg="white", bg="#166534"
        ).pack(pady=10)

        tk.Label(
            self.right_panel, text="RIGHT BANK", font=("Segoe UI", 16, "bold"),
            fg="white", bg="#166534"
        ).pack(pady=10)

        self.left_items_frame = tk.Frame(self.left_panel, bg="#166534")
        self.left_items_frame.pack(fill="both", expand=True, pady=10)

        self.right_items_frame = tk.Frame(self.right_panel, bg="#166534")
        self.right_items_frame.pack(fill="both", expand=True, pady=10)

        # River canvas
        self.canvas = tk.Canvas(center_panel, width=430, height=450, bg="#38bdf8", highlightthickness=0)
        self.canvas.pack()

        self.draw_river_scene()

        # Side panel contents
        tk.Label(
            side_panel, text="CONTROLS", font=("Segoe UI", 16, "bold"),
            fg="white", bg="#1e293b"
        ).pack(pady=12)

        self.status_label = tk.Label(
            side_panel,
            text="Game started!",
            font=("Segoe UI", 12, "bold"),
            fg="#22c55e",
            bg="#1e293b",
            wraplength=240,
            justify="center"
        )
        self.status_label.pack(pady=8)

        self.turn_label = tk.Label(
            side_panel,
            text="Boat is on LEFT side",
            font=("Segoe UI", 11),
            fg="#e2e8f0",
            bg="#1e293b"
        )
        self.turn_label.pack(pady=6)

        button_frame = tk.Frame(side_panel, bg="#1e293b")
        button_frame.pack(pady=10)

        self.buttons = {}

        button_data = [
            ("Farmer Alone", "None", "#475569"),
            ("Take Wolf", "Wolf", "#64748b"),
            ("Take Goat", "Goat", "#ca8a04"),
            ("Take Cabbage", "Cabbage", "#16a34a"),
        ]

        for text, value, color in button_data:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Segoe UI", 11, "bold"),
                width=18,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                command=lambda v=value: self.handle_move(v)
            )
            btn.pack(pady=6)
            self.buttons[value] = btn

        self.restart_button = tk.Button(
            side_panel,
            text="Restart Game",
            font=("Segoe UI", 11, "bold"),
            width=18,
            bg="#dc2626",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.restart_game
        )
        self.restart_button.pack(pady=10)

        tk.Label(
            side_panel, text="MOVE HISTORY", font=("Segoe UI", 14, "bold"),
            fg="white", bg="#1e293b"
        ).pack(pady=(12, 6))

        self.history_box = tk.Text(
            side_panel,
            width=28,
            height=12,
            font=("Consolas", 10),
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="white",
            state="disabled",
            relief="flat"
        )
        self.history_box.pack(pady=5)

    def draw_river_scene(self):
        self.canvas.delete("all")

        # sky strip
        self.canvas.create_rectangle(0, 0, 430, 80, fill="#7dd3fc", outline="")
        # river
        self.canvas.create_rectangle(0, 80, 430, 450, fill="#38bdf8", outline="")

        # small waves
        for y in range(110, 430, 35):
            for x in range(20, 420, 50):
                self.canvas.create_arc(x, y, x + 30, y + 12, start=0, extent=180, style="arc", width=2, outline="#e0f2fe")

        # banks hint
        self.canvas.create_rectangle(0, 360, 70, 450, fill="#65a30d", outline="")
        self.canvas.create_rectangle(360, 360, 430, 450, fill="#65a30d", outline="")

        self.boat_x = 80 if self.game.farmer_side == "left" else 250
        self.boat_y = 280

        self.boat = self.canvas.create_rectangle(
            self.boat_x, self.boat_y, self.boat_x + 95, self.boat_y + 35,
            fill="#7c2d12", outline="black", width=2
        )
        self.boat_text = self.canvas.create_text(
            self.boat_x + 47, self.boat_y + 17,
            text="🚣",
            font=("Segoe UI Emoji", 20)
        )

    def update_bank_items(self):
        for widget in self.left_items_frame.winfo_children():
            widget.destroy()
        for widget in self.right_items_frame.winfo_children():
            widget.destroy()

        left_sorted = sorted(self.game.left)
        right_sorted = sorted(self.game.right)

        for item in left_sorted:
            self.create_item_card(self.left_items_frame, item)

        for item in right_sorted:
            self.create_item_card(self.right_items_frame, item)

    def create_item_card(self, parent, item):
        card = tk.Frame(parent, bg=self.item_colors[item], bd=2, relief="raised")
        card.pack(pady=8, padx=15, fill="x")

        icon = self.item_icons[item]
        tk.Label(
            card,
            text=f"{icon}  {item}",
            font=("Segoe UI", 14, "bold"),
            bg=self.item_colors[item],
            fg="black",
            pady=8
        ).pack()

    def update_history(self):
        self.history_box.config(state="normal")
        self.history_box.delete("1.0", "end")

        if not self.game.history:
            self.history_box.insert("end", "No moves yet.")
        else:
            for i, move in enumerate(self.game.history, 1):
                self.history_box.insert("end", f"{i}. {move}\n")

        self.history_box.config(state="disabled")

    def update_buttons(self):
        possible_moves = self.game.get_possible_moves()
        for item, button in self.buttons.items():
            if item in possible_moves and not self.is_animating:
                button.config(state="normal")
            else:
                button.config(state="disabled")

    def update_display(self):
        self.update_bank_items()
        self.draw_river_scene()
        self.update_history()
        self.turn_label.config(text=f"Boat is on {self.game.farmer_side.upper()} side")
        self.update_buttons()

    def animate_boat(self, callback=None):
        target_x = 250 if self.game.farmer_side == "right" else 80
        current_coords = self.canvas.coords(self.boat)
        current_x = current_coords[0]

        if abs(current_x - target_x) <= 5:
            dx = target_x - current_x
            self.canvas.move(self.boat, dx, 0)
            self.canvas.move(self.boat_text, dx, 0)
            self.is_animating = False
            self.update_buttons()
            if callback:
                callback()
            return

        step = 5 if target_x > current_x else -5
        self.canvas.move(self.boat, step, 0)
        self.canvas.move(self.boat_text, step, 0)
        self.root.after(20, lambda: self.animate_boat(callback))

    def handle_move(self, item):
        if self.is_animating:
            return

        success, message = self.game.move(item)
        if not success:
            self.status_label.config(text=message, fg="#ef4444")
            return

        self.status_label.config(text=message, fg="#60a5fa")
        self.turn_label.config(text=f"Boat is on {self.game.farmer_side.upper()} side")
        self.update_bank_items()
        self.update_history()

        self.is_animating = True
        self.update_buttons()
        self.animate_boat(self.after_animation_check)

    def after_animation_check(self):
        valid, reason = self.game.is_valid()

        if not valid:
            self.status_label.config(text=reason, fg="#ef4444")
            self.disable_buttons()
            messagebox.showerror("Game Over", reason)
            return

        if self.game.is_won():
            self.status_label.config(text="Congratulations! You solved the puzzle.", fg="#22c55e")
            self.disable_buttons()
            messagebox.showinfo("You Won!", "Congratulations! You solved the puzzle.")
            return

        self.status_label.config(text="Choose your next move.", fg="#22c55e")
        self.update_display()

    def disable_buttons(self):
        for button in self.buttons.values():
            button.config(state="disabled")

    def restart_game(self):
        self.game.reset()
        self.is_animating = False
        self.status_label.config(text="Game restarted!", fg="#22c55e")
        self.update_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = RiverCrossingDeluxeGUI(root)
    root.mainloop()

    