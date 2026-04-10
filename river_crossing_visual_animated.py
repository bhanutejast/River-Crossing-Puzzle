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
        return ["None"] + sorted([x for x in current_bank if x != "Farmer"])


class AnimatedRiverCrossingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Animated River Crossing Puzzle")
        self.root.geometry("1200x720")
        self.root.configure(bg="#10233d")
        self.root.resizable(False, False)

        self.game = RiverCrossingGame()
        self.animating = False

        self.canvas_width = 900
        self.canvas_height = 560

        self.left_bank_x = 90
        self.right_bank_x = 730
        self.bank_y_positions = {
            "Farmer": 120,
            "Wolf": 220,
            "Goat": 320,
            "Cabbage": 420
        }

        self.boat_left_x = 270
        self.boat_right_x = 520
        self.boat_y = 360

        self.items_drawn = {}
        self.current_trip_item = None

        self.setup_ui()
        self.draw_scene()
        self.refresh_positions()

    def setup_ui(self):
        title = tk.Label(
            self.root,
            text="Animated Wolf - Goat - Cabbage River Crossing",
            font=("Segoe UI", 22, "bold"),
            bg="#10233d",
            fg="white"
        )
        title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#10233d")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(
            main_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#8ed6ff",
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, rowspan=2, padx=10)

        side = tk.Frame(main_frame, bg="#1c3557", width=250, height=560)
        side.grid(row=0, column=1, sticky="ns", padx=10)
        side.grid_propagate(False)

        tk.Label(
            side,
            text="Controls",
            font=("Segoe UI", 18, "bold"),
            bg="#1c3557",
            fg="white"
        ).pack(pady=12)

        self.status_label = tk.Label(
            side,
            text="Choose a move.",
            font=("Segoe UI", 11, "bold"),
            bg="#1c3557",
            fg="#7CFC98",
            wraplength=220,
            justify="center"
        )
        self.status_label.pack(pady=10)

        self.boat_side_label = tk.Label(
            side,
            text="Boat: LEFT",
            font=("Segoe UI", 12, "bold"),
            bg="#1c3557",
            fg="#FFD166"
        )
        self.boat_side_label.pack(pady=5)

        self.move_buttons = {}

        buttons = [
            ("Farmer Alone", "None", "#4a6078"),
            ("Take Wolf", "Wolf", "#6c7a89"),
            ("Take Goat", "Goat", "#d4a017"),
            ("Take Cabbage", "Cabbage", "#2e8b57"),
        ]

        for text, value, color in buttons:
            btn = tk.Button(
                side,
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
            btn.pack(pady=7)
            self.move_buttons[value] = btn

        tk.Button(
            side,
            text="Restart",
            font=("Segoe UI", 11, "bold"),
            width=18,
            bg="#cc3d3d",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.restart_game
        ).pack(pady=14)

        tk.Label(
            side,
            text="Move History",
            font=("Segoe UI", 14, "bold"),
            bg="#1c3557",
            fg="white"
        ).pack(pady=(10, 5))

        self.history_box = tk.Text(
            side,
            width=26,
            height=13,
            font=("Consolas", 10),
            bg="#0f1f33",
            fg="white",
            relief="flat",
            state="disabled"
        )
        self.history_box.pack(pady=5)

    def draw_scene(self):
        self.canvas.delete("all")

        # Sky
        self.canvas.create_rectangle(0, 0, self.canvas_width, 120, fill="#bfe7ff", outline="")
        # Sun
        self.canvas.create_oval(60, 30, 120, 90, fill="#ffd54f", outline="")
        # River
        self.canvas.create_rectangle(180, 100, 720, 520, fill="#3db7ff", outline="")
        # Banks
        self.canvas.create_rectangle(0, 100, 180, 520, fill="#72bf44", outline="")
        self.canvas.create_rectangle(720, 100, 900, 520, fill="#72bf44", outline="")
        # Labels
        self.canvas.create_text(90, 70, text="LEFT BANK", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(810, 70, text="RIGHT BANK", font=("Segoe UI", 16, "bold"))

        # Waves
        for y in range(130, 500, 35):
            for x in range(210, 700, 45):
                self.canvas.create_arc(
                    x, y, x + 25, y + 10,
                    start=0, extent=180,
                    style="arc", outline="white", width=2
                )

        # Boat
        boat_x = self.boat_left_x if self.game.farmer_side == "left" else self.boat_right_x
        self.boat = self.canvas.create_polygon(
            boat_x, self.boat_y,
            boat_x + 110, self.boat_y,
            boat_x + 90, self.boat_y + 35,
            boat_x + 20, self.boat_y + 35,
            fill="#7b4b2a",
            outline="black",
            width=2
        )

        self.boat_slots = {
            "Farmer": (boat_x + 35, self.boat_y - 20),
            "Item": (boat_x + 75, self.boat_y - 20)
        }

        self.draw_all_items()

    def draw_all_items(self):
        self.items_drawn.clear()
        for item in ["Farmer", "Wolf", "Goat", "Cabbage"]:
            if item == "Farmer":
                shape = self.draw_farmer(0, 0)
            elif item == "Wolf":
                shape = self.draw_wolf(0, 0)
            elif item == "Goat":
                shape = self.draw_goat(0, 0)
            else:
                shape = self.draw_cabbage(0, 0)
            self.items_drawn[item] = shape

    def draw_farmer(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 8, y, x + 32, y + 24, fill="#f4c27a", outline="black"))
        ids.append(self.canvas.create_rectangle(x + 12, y + 24, x + 28, y + 55, fill="#2f5aa8", outline="black"))
        ids.append(self.canvas.create_line(x + 20, y + 55, x + 10, y + 78, width=3))
        ids.append(self.canvas.create_line(x + 20, y + 55, x + 30, y + 78, width=3))
        ids.append(self.canvas.create_line(x + 12, y + 35, x, y + 55, width=3))
        ids.append(self.canvas.create_line(x + 28, y + 35, x + 40, y + 55, width=3))
        ids.append(self.canvas.create_text(x + 20, y + 92, text="Farmer", font=("Segoe UI", 10, "bold")))
        return ids

    def draw_wolf(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 5, y + 20, x + 65, y + 55, fill="#808a93", outline="black"))
        ids.append(self.canvas.create_oval(x + 50, y + 10, x + 80, y + 35, fill="#808a93", outline="black"))
        ids.append(self.canvas.create_polygon(x + 55, y + 10, x + 62, y, x + 67, y + 12, fill="#808a93", outline="black"))
        ids.append(self.canvas.create_polygon(x + 68, y + 10, x + 75, y, x + 78, y + 12, fill="#808a93", outline="black"))
        ids.append(self.canvas.create_line(x + 15, y + 55, x + 15, y + 72, width=3))
        ids.append(self.canvas.create_line(x + 30, y + 55, x + 30, y + 72, width=3))
        ids.append(self.canvas.create_line(x + 48, y + 55, x + 48, y + 72, width=3))
        ids.append(self.canvas.create_line(x + 60, y + 55, x + 60, y + 72, width=3))
        ids.append(self.canvas.create_text(x + 40, y + 88, text="Wolf", font=("Segoe UI", 10, "bold")))
        return ids

    def draw_goat(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 8, y + 20, x + 62, y + 52, fill="#f4e2b8", outline="black"))
        ids.append(self.canvas.create_oval(x + 50, y + 12, x + 78, y + 35, fill="#f4e2b8", outline="black"))
        ids.append(self.canvas.create_line(x + 58, y + 12, x + 52, y, width=2))
        ids.append(self.canvas.create_line(x + 70, y + 12, x + 76, y, width=2))
        ids.append(self.canvas.create_line(x + 18, y + 52, x + 18, y + 72, width=3))
        ids.append(self.canvas.create_line(x + 32, y + 52, x + 32, y + 72, width=3))
        ids.append(self.canvas.create_line(x + 46, y + 52, x + 46, y + 72, width=3))
        ids.append(self.canvas.create_line(x + 56, y + 52, x + 56, y + 72, width=3))
        ids.append(self.canvas.create_text(x + 40, y + 88, text="Goat", font=("Segoe UI", 10, "bold")))
        return ids

    def draw_cabbage(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 8, y + 10, x + 60, y + 62, fill="#42b649", outline="black", width=2))
        ids.append(self.canvas.create_oval(x + 16, y + 18, x + 52, y + 54, fill="#63d16a", outline=""))
        ids.append(self.canvas.create_text(x + 34, y + 82, text="Cabbage", font=("Segoe UI", 10, "bold")))
        return ids

    def move_shape_to(self, item, target_x, target_y):
        ids = self.items_drawn[item]
        bbox = self.canvas.bbox(ids[0])
        if bbox is None:
            return
        current_x = bbox[0]
        current_y = bbox[1]
        dx = target_x - current_x
        dy = target_y - current_y
        for shape_id in ids:
            self.canvas.move(shape_id, dx, dy)

    def refresh_positions(self):
        boat_x = self.boat_left_x if self.game.farmer_side == "left" else self.boat_right_x
        self.boat_slots = {
            "Farmer": (boat_x + 25, self.boat_y - 20),
            "Item": (boat_x + 65, self.boat_y - 20)
        }

        for item in ["Farmer", "Wolf", "Goat", "Cabbage"]:
            if item in self.game.left:
                self.move_shape_to(item, self.left_bank_x, self.bank_y_positions[item])
            elif item in self.game.right:
                self.move_shape_to(item, self.right_bank_x, self.bank_y_positions[item])

        self.boat_side_label.config(text=f"Boat: {self.game.farmer_side.upper()}")
        self.update_history()
        self.update_buttons()

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
        possible = self.game.get_possible_moves()
        for item, btn in self.move_buttons.items():
            btn.config(state="disabled" if self.animating else ("normal" if item in possible else "disabled"))

    def handle_move(self, item):
        if self.animating:
            return

        current_side_before = self.game.farmer_side
        success, msg = self.game.move(item)
        if not success:
            self.status_label.config(text=msg, fg="red")
            return

        self.status_label.config(text=msg, fg="#9cffba")
        self.animating = True
        self.update_buttons()

        start_x = self.boat_left_x if current_side_before == "left" else self.boat_right_x
        end_x = self.boat_right_x if current_side_before == "left" else self.boat_left_x

        # put farmer and item onto boat first
        self.move_shape_to("Farmer", start_x + 25, self.boat_y - 20)
        if item != "None":
            self.move_shape_to(item, start_x + 65, self.boat_y - 20)
            self.current_trip_item = item
        else:
            self.current_trip_item = None

        self.animate_boat(start_x, end_x)

    def animate_boat(self, current_x, target_x):
        diff = target_x - current_x

        if abs(diff) <= 4:
            dx = diff
            self.canvas.move(self.boat, dx, 0)
            for shape_id in self.items_drawn["Farmer"]:
                self.canvas.move(shape_id, dx, 0)
            if self.current_trip_item:
                for shape_id in self.items_drawn[self.current_trip_item]:
                    self.canvas.move(shape_id, dx, 0)

            self.after_animation()
            return

        step = 5 if diff > 0 else -5
        self.canvas.move(self.boat, step, 0)
        for shape_id in self.items_drawn["Farmer"]:
            self.canvas.move(shape_id, step, 0)
        if self.current_trip_item:
            for shape_id in self.items_drawn[self.current_trip_item]:
                self.canvas.move(shape_id, step, 0)

        self.root.after(20, lambda: self.animate_boat(current_x + step, target_x))

    def after_animation(self):
        self.draw_scene()
        self.refresh_positions()

        valid, reason = self.game.is_valid()
        if not valid:
            self.status_label.config(text=reason, fg="red")
            self.animating = False
            self.update_buttons()
            messagebox.showerror("Game Over", reason)
            return

        if self.game.is_won():
            self.status_label.config(text="Congratulations! You solved the puzzle.", fg="#7CFC98")
            self.animating = False
            self.update_buttons()
            messagebox.showinfo("You Won", "Congratulations! You solved the puzzle.")
            return

        self.animating = False
        self.update_buttons()

    def restart_game(self):
        if self.animating:
            return
        self.game.reset()
        self.status_label.config(text="Game restarted.", fg="#7CFC98")
        self.draw_scene()
        self.refresh_positions()


if __name__ == "__main__":
    root = tk.Tk()
    app = AnimatedRiverCrossingGUI(root)
    root.mainloop()