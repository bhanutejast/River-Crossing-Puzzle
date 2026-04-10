import tkinter as tk
from tkinter import messagebox
import math


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


class RiverCrossingUltimateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("River Crossing Puzzle - Ultimate Animated Edition")
        self.root.geometry("1300x760")
        self.root.configure(bg="#0f1b2d")
        self.root.resizable(False, False)

        self.game = RiverCrossingGame()
        self.animating = False

        self.canvas_width = 980
        self.canvas_height = 620

        self.left_bank_item_x = 70
        self.right_bank_item_x = 835
        self.left_bank_edge_x = 190
        self.right_bank_edge_x = 790

        self.boat_left_x = 285
        self.boat_right_x = 560
        self.boat_y = 400

        self.bank_y_positions = {
            "Farmer": 130,
            "Wolf": 240,
            "Goat": 350,
            "Cabbage": 470
        }

        self.items_drawn = {}
        self.trip_item = None
        self.trip_side_before = "left"

        self.wave_phase = 0
        self.boat_bob_phase = 0
        self.water_job = None
        self.idle_job = None

        self.setup_ui()
        self.draw_scene()
        self.refresh_positions()
        self.animate_environment()

    def setup_ui(self):
        title = tk.Label(
            self.root,
            text="River Crossing Puzzle - Ultimate Animated Edition",
            font=("Segoe UI", 24, "bold"),
            bg="#0f1b2d",
            fg="white"
        )
        title.pack(pady=10)

        main = tk.Frame(self.root, bg="#0f1b2d")
        main.pack(fill="both", expand=True, padx=12, pady=10)

        self.canvas = tk.Canvas(
            main,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#9ad8ff",
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, padx=(0, 14))

        side = tk.Frame(main, bg="#162842", width=260, height=self.canvas_height)
        side.grid(row=0, column=1, sticky="ns")
        side.grid_propagate(False)

        tk.Label(
            side,
            text="Control Panel",
            font=("Segoe UI", 19, "bold"),
            bg="#162842",
            fg="white"
        ).pack(pady=14)

        self.status_label = tk.Label(
            side,
            text="Choose a move.",
            font=("Segoe UI", 11, "bold"),
            bg="#162842",
            fg="#8df7b8",
            wraplength=220,
            justify="center"
        )
        self.status_label.pack(pady=8)

        self.boat_label = tk.Label(
            side,
            text="Boat: LEFT",
            font=("Segoe UI", 12, "bold"),
            bg="#162842",
            fg="#ffd166"
        )
        self.boat_label.pack(pady=5)

        self.move_buttons = {}
        btn_info = [
            ("Farmer Alone", "None", "#475569"),
            ("Take Wolf", "Wolf", "#6b7280"),
            ("Take Goat", "Goat", "#ca8a04"),
            ("Take Cabbage", "Cabbage", "#16a34a"),
        ]

        for text, value, color in btn_info:
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
            bg="#dc2626",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.restart_game
        ).pack(pady=14)

        tk.Label(
            side,
            text="Move History",
            font=("Segoe UI", 14, "bold"),
            bg="#162842",
            fg="white"
        ).pack(pady=(12, 6))

        self.history_box = tk.Text(
            side,
            width=28,
            height=15,
            font=("Consolas", 10),
            bg="#0c1524",
            fg="white",
            relief="flat",
            state="disabled"
        )
        self.history_box.pack(pady=5)

    def draw_scene(self):
        self.canvas.delete("all")

        # Sky
        self.canvas.create_rectangle(0, 0, self.canvas_width, 140, fill="#c9ebff", outline="")
        self.canvas.create_oval(70, 30, 140, 100, fill="#ffd54f", outline="")
        self.canvas.create_text(105, 65, text="☀", font=("Segoe UI Emoji", 20))

        # Clouds
        self.draw_cloud(220, 45)
        self.draw_cloud(530, 35)
        self.draw_cloud(760, 55)

        # River
        self.canvas.create_rectangle(190, 120, 790, 585, fill="#39a9ff", outline="")

        # Banks
        self.canvas.create_rectangle(0, 120, 190, 585, fill="#79c85b", outline="")
        self.canvas.create_rectangle(790, 120, 980, 585, fill="#79c85b", outline="")

        # Shore lines
        self.canvas.create_line(190, 120, 190, 585, fill="#d4b483", width=4)
        self.canvas.create_line(790, 120, 790, 585, fill="#d4b483", width=4)

        self.canvas.create_text(95, 85, text="LEFT BANK", font=("Segoe UI", 17, "bold"))
        self.canvas.create_text(885, 85, text="RIGHT BANK", font=("Segoe UI", 17, "bold"))

        self.draw_waves()
        self.draw_boat()
        self.draw_all_items()

    def draw_cloud(self, x, y):
        self.canvas.create_oval(x, y, x + 55, y + 35, fill="white", outline="")
        self.canvas.create_oval(x + 25, y - 10, x + 85, y + 30, fill="white", outline="")
        self.canvas.create_oval(x + 55, y, x + 110, y + 35, fill="white", outline="")

    def draw_waves(self):
        for y in range(150, 560, 30):
            shift = (self.wave_phase + y // 8) % 38
            for x in range(210, 760, 42):
                self.canvas.create_arc(
                    x + shift, y, x + shift + 25, y + 10,
                    start=0, extent=180, style="arc",
                    outline="#e8f7ff", width=2
                )

    def draw_boat(self):
        boat_x = self.boat_left_x if self.game.farmer_side == "left" else self.boat_right_x
        bob = math.sin(self.boat_bob_phase) * 3
        y = self.boat_y + bob

        self.boat = self.canvas.create_polygon(
            boat_x, y,
            boat_x + 120, y,
            boat_x + 95, y + 38,
            boat_x + 20, y + 38,
            fill="#7c4a28",
            outline="#3a2416",
            width=2
        )

        self.boat_mast = self.canvas.create_line(boat_x + 50, y, boat_x + 50, y - 55, width=3, fill="#5a3820")
        self.boat_sail = self.canvas.create_polygon(
            boat_x + 52, y - 55,
            boat_x + 52, y - 10,
            boat_x + 95, y - 30,
            fill="#fff7d6",
            outline="#c9c1a1"
        )

        self.boat_slots = {
            "Farmer": (boat_x + 18, y - 35),
            "Item": (boat_x + 65, y - 30)
        }

    def draw_all_items(self):
        self.items_drawn.clear()
        for item in ["Farmer", "Wolf", "Goat", "Cabbage"]:
            if item == "Farmer":
                ids = self.draw_farmer(0, 0)
            elif item == "Wolf":
                ids = self.draw_wolf(0, 0)
            elif item == "Goat":
                ids = self.draw_goat(0, 0)
            else:
                ids = self.draw_cabbage(0, 0)
            self.items_drawn[item] = ids

    def draw_farmer(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 10, y, x + 34, y + 24, fill="#f3c78a", outline="black"))
        ids.append(self.canvas.create_arc(x + 6, y - 4, x + 38, y + 18, start=0, extent=180, fill="#8b5a2b", outline="black"))
        ids.append(self.canvas.create_rectangle(x + 13, y + 24, x + 30, y + 57, fill="#2e65b0", outline="black"))
        ids.append(self.canvas.create_line(x + 20, y + 57, x + 10, y + 82, width=3))
        ids.append(self.canvas.create_line(x + 22, y + 57, x + 32, y + 82, width=3))
        ids.append(self.canvas.create_line(x + 13, y + 35, x + 0, y + 55, width=3))
        ids.append(self.canvas.create_line(x + 30, y + 35, x + 42, y + 55, width=3))
        ids.append(self.canvas.create_text(x + 22, y + 96, text="Farmer", font=("Segoe UI", 10, "bold")))
        return ids

    def draw_wolf(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 8, y + 20, x + 74, y + 58, fill="#7f8790", outline="black"))
        ids.append(self.canvas.create_oval(x + 54, y + 8, x + 86, y + 34, fill="#7f8790", outline="black"))
        ids.append(self.canvas.create_polygon(x + 58, y + 10, x + 64, y - 2, x + 69, y + 12, fill="#7f8790", outline="black"))
        ids.append(self.canvas.create_polygon(x + 71, y + 10, x + 77, y - 2, x + 82, y + 12, fill="#7f8790", outline="black"))
        ids.append(self.canvas.create_line(x + 16, y + 58, x + 16, y + 78, width=3))
        ids.append(self.canvas.create_line(x + 30, y + 58, x + 30, y + 78, width=3))
        ids.append(self.canvas.create_line(x + 50, y + 58, x + 50, y + 78, width=3))
        ids.append(self.canvas.create_line(x + 64, y + 58, x + 64, y + 78, width=3))
        ids.append(self.canvas.create_line(x + 8, y + 30, x - 10, y + 18, width=3))
        ids.append(self.canvas.create_text(x + 40, y + 94, text="Wolf", font=("Segoe UI", 10, "bold")))
        return ids

    def draw_goat(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 10, y + 22, x + 70, y + 58, fill="#f0e0bf", outline="black"))
        ids.append(self.canvas.create_oval(x + 54, y + 10, x + 84, y + 35, fill="#f0e0bf", outline="black"))
        ids.append(self.canvas.create_line(x + 60, y + 10, x + 54, y - 2, width=2))
        ids.append(self.canvas.create_line(x + 74, y + 10, x + 80, y - 2, width=2))
        ids.append(self.canvas.create_line(x + 18, y + 58, x + 18, y + 80, width=3))
        ids.append(self.canvas.create_line(x + 32, y + 58, x + 32, y + 80, width=3))
        ids.append(self.canvas.create_line(x + 48, y + 58, x + 48, y + 80, width=3))
        ids.append(self.canvas.create_line(x + 60, y + 58, x + 60, y + 80, width=3))
        ids.append(self.canvas.create_line(x + 10, y + 30, x - 8, y + 20, width=2))
        ids.append(self.canvas.create_text(x + 40, y + 96, text="Goat", font=("Segoe UI", 10, "bold")))
        return ids

    def draw_cabbage(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 10, y + 10, x + 65, y + 65, fill="#3dbb4a", outline="black", width=2))
        ids.append(self.canvas.create_oval(x + 17, y + 17, x + 58, y + 58, fill="#6ad971", outline=""))
        ids.append(self.canvas.create_arc(x + 18, y + 18, x + 56, y + 56, start=30, extent=110, style="arc", width=2))
        ids.append(self.canvas.create_arc(x + 18, y + 18, x + 56, y + 56, start=170, extent=100, style="arc", width=2))
        ids.append(self.canvas.create_text(x + 38, y + 88, text="Cabbage", font=("Segoe UI", 10, "bold")))
        return ids

    def get_bbox_top_left(self, item):
        bbox = self.canvas.bbox(self.items_drawn[item][0])
        return bbox[0], bbox[1]

    def move_shape_by(self, item, dx, dy):
        for sid in self.items_drawn[item]:
            self.canvas.move(sid, dx, dy)

    def move_shape_to(self, item, target_x, target_y):
        cx, cy = self.get_bbox_top_left(item)
        self.move_shape_by(item, target_x - cx, target_y - cy)

    def refresh_positions(self):
        for item in ["Farmer", "Wolf", "Goat", "Cabbage"]:
            if item in self.game.left:
                self.move_shape_to(item, self.left_bank_item_x, self.bank_y_positions[item])
            elif item in self.game.right:
                self.move_shape_to(item, self.right_bank_item_x, self.bank_y_positions[item])

        self.boat_label.config(text=f"Boat: {self.game.farmer_side.upper()}")
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
            if self.animating:
                btn.config(state="disabled")
            else:
                btn.config(state="normal" if item in possible else "disabled")

    def animate_environment(self):
        self.wave_phase = (self.wave_phase + 3) % 40
        self.boat_bob_phase += 0.18

        if not self.animating:
            self.draw_scene()
            self.refresh_positions()
            self.apply_idle_animation()

        self.root.after(120, self.animate_environment)

    def apply_idle_animation(self):
        if "Goat" in self.items_drawn:
            wobble = math.sin(self.boat_bob_phase * 2.2) * 1.5
            self.move_shape_by("Goat", 0, wobble * 0.15)

        if "Wolf" in self.items_drawn:
            wag = math.sin(self.boat_bob_phase * 1.8) * 0.12
            self.move_shape_by("Wolf", wag, 0)

    def handle_move(self, item):
        if self.animating:
            return

        self.trip_side_before = self.game.farmer_side
        success, msg = self.game.move(item)
        if not success:
            self.status_label.config(text=msg, fg="red")
            return

        self.trip_item = None if item == "None" else item
        self.status_label.config(text=msg, fg="#8df7b8")
        self.animating = True
        self.update_buttons()

        self.walk_to_boat(item)

    def walk_to_boat(self, item):
        start_side = self.trip_side_before
        target_x_farmer = self.left_bank_edge_x if start_side == "left" else self.right_bank_edge_x - 25
        target_x_item = self.left_bank_edge_x - 25 if start_side == "left" else self.right_bank_edge_x - 50

        def step():
            done_farmer = self.step_towards_x("Farmer", target_x_farmer, 5)
            done_item = True

            if item != "None":
                done_item = self.step_towards_x(item, target_x_item, 5)

            if done_farmer and done_item:
                self.board_boat(item)
            else:
                self.root.after(20, step)

        step()

    def board_boat(self, item):
        start_x = self.boat_left_x if self.trip_side_before == "left" else self.boat_right_x

        self.move_shape_to("Farmer", start_x + 16, self.boat_y - 42)
        if item != "None":
            self.move_shape_to(item, start_x + 68, self.boat_y - 34)

        self.root.after(200, lambda: self.animate_boat_crossing(item))

    def animate_boat_crossing(self, item):
        current_x = self.boat_left_x if self.trip_side_before == "left" else self.boat_right_x
        target_x = self.boat_right_x if self.trip_side_before == "left" else self.boat_left_x

        def step():
            nonlocal current_x
            diff = target_x - current_x
            if abs(diff) <= 5:
                dx = diff
                self.move_boat_group(dx)
                self.finish_crossing(item)
                return

            dx = 6 if diff > 0 else -6
            current_x += dx
            self.move_boat_group(dx)
            self.root.after(20, step)

        step()

    def move_boat_group(self, dx):
        self.canvas.move(self.boat, dx, 0)
        self.canvas.move(self.boat_mast, dx, 0)
        self.canvas.move(self.boat_sail, dx, 0)
        self.move_shape_by("Farmer", dx, 0)
        if self.trip_item:
            self.move_shape_by(self.trip_item, dx, 0)

    def finish_crossing(self, item):
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
            self.status_label.config(text="Congratulations! You solved the puzzle.", fg="#8df7b8")
            self.animating = False
            self.update_buttons()
            messagebox.showinfo("You Won", "Congratulations! You solved the puzzle.")
            return

        self.status_label.config(text="Choose the next move.", fg="#8df7b8")
        self.animating = False
        self.update_buttons()

    def step_towards_x(self, item, target_x, speed):
        current_x, _ = self.get_bbox_top_left(item)
        diff = target_x - current_x
        if abs(diff) <= speed:
            self.move_shape_by(item, diff, 0)
            return True

        dx = speed if diff > 0 else -speed
        self.move_shape_by(item, dx, 0)
        return False

    def restart_game(self):
        if self.animating:
            return
        self.game.reset()
        self.trip_item = None
        self.status_label.config(text="Game restarted.", fg="#8df7b8")
        self.draw_scene()
        self.refresh_positions()


if __name__ == "__main__":
    root = tk.Tk()
    app = RiverCrossingUltimateGUI(root)
    root.mainloop()
    