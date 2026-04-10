import tkinter as tk
from tkinter import messagebox
import time


class RiverCrossingGame:
    def __init__(self):
        self.solution_steps = ["Goat", "None", "Wolf", "Goat", "Cabbage", "None", "Goat"]
        self.reset()

    def reset(self):
        self.left = {"Farmer", "Wolf", "Goat", "Cabbage"}
        self.right = set()
        self.farmer_side = "left"
        self.history = []
        self.move_count = 0

    def is_valid(self):
        if "Farmer" not in self.left:
            if "Wolf" in self.left and "Goat" in self.left:
                return False, "The wolf ate the goat on the LEFT bank."
            if "Goat" in self.left and "Cabbage" in self.left:
                return False, "The goat ate the cabbage on the LEFT bank."

        if "Farmer" not in self.right:
            if "Wolf" in self.right and "Goat" in self.right:
                return False, "The wolf ate the goat on the RIGHT bank."
            if "Goat" in self.right and "Cabbage" in self.right:
                return False, "The goat ate the cabbage on the RIGHT bank."

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
            move_text = f"Farmer takes {item}"
        else:
            move_text = "Farmer goes alone"

        self.farmer_side = "right" if self.farmer_side == "left" else "left"
        self.history.append(move_text)
        self.move_count += 1
        return True, move_text

    def get_possible_moves(self):
        current_bank = self.left if self.farmer_side == "left" else self.right
        items = [item for item in current_bank if item != "Farmer"]
        return ["None"] + sorted(items)

    def next_hint(self):
        if len(self.history) < len(self.solution_steps):
            nxt = self.solution_steps[len(self.history)]
            return "Hint: Farmer should go alone next." if nxt == "None" else f"Hint: Take {nxt} next."
        return "No hint available."

    def get_solution_text(self):
        readable = []
        for step in self.solution_steps:
            if step == "None":
                readable.append("Farmer goes alone")
            else:
                readable.append(f"Farmer takes {step}")
        return readable


class RiverCrossingProGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("River Crossing Puzzle - Pro Edition")
        self.root.geometry("1380x820")
        self.root.minsize(1380, 820)
        self.root.configure(bg="#0b1020")

        self.game = RiverCrossingGame()
        self.is_animating = False
        self.demo_running = False
        self.start_time = time.time()
        self.wave_offset = 0

        self.icons = {
            "Farmer": "👨‍🌾",
            "Wolf": "🐺",
            "Goat": "🐐",
            "Cabbage": "🥬"
        }

        self.item_colors = {
            "Farmer": "#f59e0b",
            "Wolf": "#64748b",
            "Goat": "#eab308",
            "Cabbage": "#22c55e"
        }

        self.setup_ui()
        self.update_display()
        self.update_timer()
        self.animate_water()

    def setup_ui(self):
        self.header = tk.Frame(self.root, bg="#121a2f", height=78)
        self.header.pack(fill="x")

        title = tk.Label(
            self.header,
            text="River Crossing Puzzle • Pro Edition",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg="#121a2f"
        )
        title.pack(side="left", padx=25, pady=18)

        self.header_status = tk.Label(
            self.header,
            text="Professional Interactive Puzzle Simulator",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#121a2f"
        )
        self.header_status.pack(side="right", padx=25)

        self.main = tk.Frame(self.root, bg="#0b1020")
        self.main.pack(fill="both", expand=True, padx=16, pady=16)

        self.left_bank_panel = tk.Frame(self.main, bg="#122c1d", width=250, bd=0, highlightbackground="#1f5132", highlightthickness=2)
        self.left_bank_panel.grid(row=0, column=0, sticky="ns", padx=(0, 12))
        self.left_bank_panel.grid_propagate(False)

        self.center_panel = tk.Frame(self.main, bg="#0b1020")
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=4)

        self.right_bank_panel = tk.Frame(self.main, bg="#122c1d", width=250, bd=0, highlightbackground="#1f5132", highlightthickness=2)
        self.right_bank_panel.grid(row=0, column=2, sticky="ns", padx=(12, 12))
        self.right_bank_panel.grid_propagate(False)

        self.side_panel = tk.Frame(self.main, bg="#121a2f", width=360, bd=0, highlightbackground="#24304f", highlightthickness=2)
        self.side_panel.grid(row=0, column=3, sticky="ns")
        self.side_panel.grid_propagate(False)

        self.main.grid_columnconfigure(1, weight=1)
        self.main.grid_rowconfigure(0, weight=1)

        self.build_bank_panel(self.left_bank_panel, "LEFT BANK")
        self.build_bank_panel(self.right_bank_panel, "RIGHT BANK")

        self.left_items_area = tk.Frame(self.left_bank_panel, bg="#122c1d")
        self.left_items_area.pack(fill="both", expand=True, padx=14, pady=(6, 14))

        self.right_items_area = tk.Frame(self.right_bank_panel, bg="#122c1d")
        self.right_items_area.pack(fill="both", expand=True, padx=14, pady=(6, 14))

        self.build_center_canvas()
        self.build_side_panel()

    def build_bank_panel(self, parent, title_text):
        title = tk.Label(
            parent,
            text=title_text,
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#122c1d"
        )
        title.pack(pady=(16, 4))

        sub = tk.Label(
            parent,
            text="Entities currently on this side",
            font=("Segoe UI", 10),
            fg="#b7d6c0",
            bg="#122c1d"
        )
        sub.pack(pady=(0, 8))

    def build_center_canvas(self):
        self.canvas_card = tk.Frame(self.center_panel, bg="#121a2f", highlightbackground="#24304f", highlightthickness=2)
        self.canvas_card.pack(fill="both", expand=True)

        top_bar = tk.Frame(self.canvas_card, bg="#121a2f", height=58)
        top_bar.pack(fill="x")

        self.scene_status = tk.Label(
            top_bar,
            text="Boat ready on LEFT side",
            font=("Segoe UI", 12, "bold"),
            fg="#e2e8f0",
            bg="#121a2f"
        )
        self.scene_status.pack(side="left", padx=18, pady=14)

        self.canvas = tk.Canvas(self.canvas_card, width=700, height=660, bg="#52b5ff", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.draw_scene()

    def build_side_panel(self):
        heading = tk.Label(
            self.side_panel,
            text="CONTROL CENTER",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#121a2f"
        )
        heading.pack(pady=(16, 8))

        self.status_box = tk.Label(
            self.side_panel,
            text="Welcome! Move all items safely across the river.",
            font=("Segoe UI", 11, "bold"),
            fg="#4ade80",
            bg="#121a2f",
            wraplength=310,
            justify="center"
        )
        self.status_box.pack(pady=(2, 14))

        stats_frame = tk.Frame(self.side_panel, bg="#121a2f")
        stats_frame.pack(fill="x", padx=18, pady=(0, 10))

        self.timer_label = self.make_stat_card(stats_frame, "TIME", "00:00", 0, 0)
        self.moves_label = self.make_stat_card(stats_frame, "MOVES", "0", 0, 1)
        self.boat_label = self.make_stat_card(stats_frame, "BOAT SIDE", "LEFT", 1, 0)
        self.state_label = self.make_stat_card(stats_frame, "STATE", "ACTIVE", 1, 1)

        controls_label = tk.Label(
            self.side_panel,
            text="MOVES",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#121a2f"
        )
        controls_label.pack(pady=(8, 8))

        button_frame = tk.Frame(self.side_panel, bg="#121a2f")
        button_frame.pack(pady=(0, 8))

        self.move_buttons = {}

        btn_specs = [
            ("Farmer Alone", "None", "#475569"),
            ("Take Wolf", "Wolf", "#64748b"),
            ("Take Goat", "Goat", "#ca8a04"),
            ("Take Cabbage", "Cabbage", "#16a34a"),
        ]

        for text, item, color in btn_specs:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Segoe UI", 11, "bold"),
                width=22,
                height=1,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda x=item: self.handle_player_move(x)
            )
            btn.pack(pady=5)
            self.move_buttons[item] = btn

        utility_frame = tk.Frame(self.side_panel, bg="#121a2f")
        utility_frame.pack(pady=(8, 10))

        self.hint_btn = tk.Button(
            utility_frame,
            text="Hint",
            width=10,
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.show_hint
        )
        self.hint_btn.grid(row=0, column=0, padx=5, pady=5)

        self.demo_btn = tk.Button(
            utility_frame,
            text="Auto Solve",
            width=10,
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.start_demo
        )
        self.demo_btn.grid(row=0, column=1, padx=5, pady=5)

        self.restart_btn = tk.Button(
            utility_frame,
            text="Restart",
            width=10,
            font=("Segoe UI", 10, "bold"),
            bg="#dc2626",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.restart_game
        )
        self.restart_btn.grid(row=0, column=2, padx=5, pady=5)

        history_label = tk.Label(
            self.side_panel,
            text="MOVE HISTORY",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#121a2f"
        )
        history_label.pack(pady=(10, 6))

        self.history_box = tk.Text(
            self.side_panel,
            width=36,
            height=13,
            font=("Consolas", 10),
            bg="#0b1020",
            fg="#e2e8f0",
            insertbackground="white",
            relief="flat",
            bd=0,
            state="disabled"
        )
        self.history_box.pack(padx=18, pady=(0, 12))

        legend_label = tk.Label(
            self.side_panel,
            text="RULES",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#121a2f"
        )
        legend_label.pack(pady=(2, 6))

        rules = tk.Label(
            self.side_panel,
            text="• Boat carries Farmer + one item\n• Wolf cannot stay with Goat unattended\n• Goat cannot stay with Cabbage unattended",
            font=("Segoe UI", 10),
            fg="#cbd5e1",
            bg="#121a2f",
            justify="left",
            wraplength=300
        )
        rules.pack(padx=20, pady=(0, 12))

    def make_stat_card(self, parent, title, value, row, col):
        card = tk.Frame(parent, bg="#0b1020", highlightbackground="#24304f", highlightthickness=1)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#0b1020").pack(pady=(8, 2))
        value_label = tk.Label(card, text=value, font=("Segoe UI", 14, "bold"), fg="white", bg="#0b1020")
        value_label.pack(pady=(0, 8))
        return value_label

    def draw_scene(self):
        self.canvas.delete("all")

        width = int(self.canvas.winfo_width() or 700)
        height = int(self.canvas.winfo_height() or 660)

        self.canvas.create_rectangle(0, 0, width, 140, fill="#8fd3ff", outline="")
        self.canvas.create_rectangle(0, 140, width, height, fill="#48b8ff", outline="")

        self.canvas.create_rectangle(0, height - 130, 120, height, fill="#74b816", outline="")
        self.canvas.create_rectangle(width - 120, height - 130, width, height, fill="#74b816", outline="")

        self.canvas.create_oval(55, 35, 115, 95, fill="#ffd54a", outline="")
        self.canvas.create_text(85, 65, text="☀", font=("Segoe UI Emoji", 18))

        for i in range(8):
            x1 = 50 + i * 80
            self.canvas.create_oval(x1, 25, x1 + 55, 55, fill="#dff4ff", outline="")
            self.canvas.create_oval(x1 + 25, 15, x1 + 85, 50, fill="#dff4ff", outline="")

        self.draw_waves(width, height)

        boat_y = height * 0.57
        self.left_boat_x = 110
        self.right_boat_x = width - 220
        boat_x = self.left_boat_x if self.game.farmer_side == "left" else self.right_boat_x

        self.boat = self.canvas.create_polygon(
            boat_x, boat_y,
            boat_x + 110, boat_y,
            boat_x + 90, boat_y + 34,
            boat_x + 18, boat_y + 34,
            fill="#7c3f14", outline="#3b1d0a", width=2
        )

        self.boat_shadow = self.canvas.create_oval(
            boat_x + 10, boat_y + 30, boat_x + 105, boat_y + 44,
            fill="#2a7fc0", outline=""
        )

        boat_text = "🚣"
        self.boat_text = self.canvas.create_text(
            boat_x + 55, boat_y + 8,
            text=boat_text,
            font=("Segoe UI Emoji", 24)
        )

    def draw_waves(self, width, height):
        base_y = 180
        for row in range(10):
            y = base_y + row * 38
            shift = (self.wave_offset + row * 11) % 40
            for x in range(-20, width + 40, 55):
                self.canvas.create_arc(
                    x + shift, y, x + shift + 28, y + 11,
                    start=0, extent=180, style="arc",
                    outline="#d7f0ff", width=2
                )

    def animate_water(self):
        self.wave_offset = (self.wave_offset + 3) % 40
        self.draw_scene()
        self.after_scene_redraw()
        self.root.after(140, self.animate_water)

    def after_scene_redraw(self):
        pass

    def create_item_cards(self, parent, items):
        for widget in parent.winfo_children():
            widget.destroy()

        sorted_items = sorted(items)
        if not sorted_items:
            blank = tk.Label(parent, text="No items here", font=("Segoe UI", 12), fg="#b7d6c0", bg="#122c1d")
            blank.pack(pady=30)
            return

        for item in sorted_items:
            color = self.item_colors[item]
            card = tk.Frame(parent, bg=color, highlightbackground="#ffffff", highlightthickness=1)
            card.pack(fill="x", pady=8)

            icon = self.icons[item]
            text = tk.Label(
                card,
                text=f"{icon}  {item}",
                font=("Segoe UI", 14, "bold"),
                bg=color,
                fg="black",
                pady=10
            )
            text.pack()

    def update_history(self):
        self.history_box.config(state="normal")
        self.history_box.delete("1.0", "end")

        if not self.game.history:
            self.history_box.insert("end", "No moves yet.\n")
        else:
            for i, move in enumerate(self.game.history, 1):
                self.history_box.insert("end", f"{i:02d}. {move}\n")

        self.history_box.config(state="disabled")

    def update_stats(self):
        self.moves_label.config(text=str(self.game.move_count))
        self.boat_label.config(text=self.game.farmer_side.upper())

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        self.root.after(1000, self.update_timer)

    def update_move_buttons(self):
        possible = self.game.get_possible_moves()

        for item, btn in self.move_buttons.items():
            if not self.is_animating and not self.demo_running and item in possible:
                btn.config(state="normal")
            else:
                btn.config(state="disabled")

        utility_state = "disabled" if self.is_animating else "normal"
        self.hint_btn.config(state=utility_state)
        self.restart_btn.config(state="normal")
        self.demo_btn.config(state="disabled" if self.demo_running else utility_state)

    def update_display(self):
        self.create_item_cards(self.left_items_area, self.game.left)
        self.create_item_cards(self.right_items_area, self.game.right)
        self.scene_status.config(text=f"Boat ready on {self.game.farmer_side.upper()} side")
        self.update_history()
        self.update_stats()
        self.update_move_buttons()

    def animate_boat_to_current_side(self, callback=None):
        current_coords = self.canvas.coords(self.boat)
        current_x = current_coords[0]
        target_x = self.left_boat_x if self.game.farmer_side == "left" else self.right_boat_x

        def step():
            nonlocal current_x
            current_coords_now = self.canvas.coords(self.boat)
            if not current_coords_now:
                return

            x = current_coords_now[0]
            diff = target_x - x

            if abs(diff) <= 6:
                dx = diff
                self.canvas.move(self.boat, dx, 0)
                self.canvas.move(self.boat_shadow, dx, 0)
                self.canvas.move(self.boat_text, dx, 0)
                self.is_animating = False
                self.update_move_buttons()
                if callback:
                    callback()
                return

            dx = 8 if diff > 0 else -8
            self.canvas.move(self.boat, dx, 0)
            self.canvas.move(self.boat_shadow, dx, 0)
            self.canvas.move(self.boat_text, dx, 0)
            self.root.after(18, step)

        step()

    def handle_player_move(self, item):
        if self.is_animating or self.demo_running:
            return

        success, msg = self.game.move(item)
        if not success:
            self.status_box.config(text=msg, fg="#ef4444")
            return

        self.status_box.config(text=msg, fg="#60a5fa")
        self.scene_status.config(text=f"Boat moving to {self.game.farmer_side.upper()} side")
        self.update_display()

        self.is_animating = True
        self.update_move_buttons()
        self.animate_boat_to_current_side(self.after_move_check)

    def after_move_check(self):
        valid, reason = self.game.is_valid()

        if not valid:
            self.state_label.config(text="FAILED", fg="#ef4444")
            self.status_box.config(text=reason, fg="#ef4444")
            self.disable_all_buttons()
            messagebox.showerror("Game Over", reason)
            self.demo_running = False
            return

        if self.game.is_won():
            self.state_label.config(text="SOLVED", fg="#22c55e")
            self.status_box.config(text="Congratulations! Puzzle solved successfully.", fg="#22c55e")
            self.disable_all_buttons()
            messagebox.showinfo("Success", "Congratulations! You solved the puzzle.")
            self.demo_running = False
            return

        self.state_label.config(text="ACTIVE", fg="white")
        self.status_box.config(text="Choose the next move.", fg="#4ade80")
        self.scene_status.config(text=f"Boat ready on {self.game.farmer_side.upper()} side")
        self.update_display()

        if self.demo_running:
            self.root.after(700, self.perform_demo_step)

    def disable_all_buttons(self):
        for btn in self.move_buttons.values():
            btn.config(state="disabled")
        self.hint_btn.config(state="disabled")
        self.demo_btn.config(state="disabled")

    def show_hint(self):
        self.status_box.config(text=self.game.next_hint(), fg="#facc15")

    def restart_game(self):
        self.demo_running = False
        self.is_animating = False
        self.game.reset()
        self.start_time = time.time()
        self.state_label.config(text="ACTIVE", fg="white")
        self.status_box.config(text="Game restarted. Good luck!", fg="#4ade80")
        self.scene_status.config(text="Boat ready on LEFT side")
        self.draw_scene()
        self.update_display()

    def start_demo(self):
        if self.is_animating:
            return

        self.restart_game()
        self.demo_running = True
        self.status_box.config(text="Auto-solve demo started.", fg="#c084fc")
        self.demo_btn.config(state="disabled")
        self.root.after(800, self.perform_demo_step)

    def perform_demo_step(self):
        if not self.demo_running or self.is_animating:
            return

        step_index = len(self.game.history)
        if step_index >= len(self.game.solution_steps):
            self.demo_running = False
            return

        next_item = self.game.solution_steps[step_index]
        self.handle_demo_move(next_item)

    def handle_demo_move(self, item):
        success, msg = self.game.move(item)
        if not success:
            self.demo_running = False
            self.status_box.config(text=msg, fg="#ef4444")
            return

        self.status_box.config(text=f"Demo: {msg}", fg="#c084fc")
        self.scene_status.config(text=f"Boat moving to {self.game.farmer_side.upper()} side")
        self.update_display()

        self.is_animating = True
        self.update_move_buttons()
        self.animate_boat_to_current_side(self.after_move_check)


if __name__ == "__main__":
    root = tk.Tk()
    app = RiverCrossingProGUI(root)
    root.mainloop()