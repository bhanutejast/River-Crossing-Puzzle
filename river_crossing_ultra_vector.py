import tkinter as tk
from tkinter import messagebox
import math
import time


# =========================================================
# GAME LOGIC
# =========================================================
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
        self.score = 100

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
            text = f"Farmer takes {item}"
        else:
            text = "Farmer goes alone"

        self.farmer_side = "right" if self.farmer_side == "left" else "left"
        self.history.append(text)
        self.move_count += 1
        self.score = max(0, self.score - 5)

        return True, text

    def get_possible_moves(self):
        current_bank = self.left if self.farmer_side == "left" else self.right
        return ["None"] + sorted([x for x in current_bank if x != "Farmer"])

    def next_hint(self):
        idx = len(self.history)
        if idx < len(self.solution_steps):
            step = self.solution_steps[idx]
            if step == "None":
                return "Farmer should go alone next."
            return f"Take {step} next."
        return "No hint available."

    def final_score(self, elapsed_seconds):
        time_bonus = max(0, 90 - elapsed_seconds)
        move_bonus = max(0, 35 - max(0, self.move_count - 7) * 5)
        return self.score + time_bonus + move_bonus


# =========================================================
# ULTRA VECTOR GUI
# =========================================================
class RiverCrossingUltraVectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("River Crossing Ultra Vector Edition")
        self.root.geometry("1450x880")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a1220")

        self.game = RiverCrossingGame()

        self.canvas_width = 980
        self.canvas_height = 700

        self.left_x = 75
        self.right_x = 850
        self.left_edge_x = 190
        self.right_edge_x = 795

        self.boat_left_x = 305
        self.boat_right_x = 560
        self.boat_y = 470

        self.bank_y = {
            "Farmer": 150,
            "Wolf": 285,
            "Goat": 430,
            "Cabbage": 575
        }

        self.day_mode = True
        self.animating = False
        self.demo_running = False
        self.start_time = None
        self.elapsed_seconds = 0
        self.timer_running = False

        self.wave_phase = 0
        self.boat_bob_phase = 0
        self.idle_phase = 0

        self.trip_item = None
        self.trip_side_before = "left"

        self.entities = {}
        self.overlay_items = []

        self.build_start_screen()

    # =========================================================
    # SCREENS
    # =========================================================
    def clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

    def build_start_screen(self):
        self.clear_root()

        frame = tk.Frame(self.root, bg="#0a1220")
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="RIVER CROSSING",
            font=("Segoe UI", 34, "bold"),
            fg="white",
            bg="#0a1220"
        ).pack(pady=(120, 8))

        tk.Label(
            frame,
            text="ULTRA VECTOR EDITION",
            font=("Segoe UI", 20, "bold"),
            fg="#60a5fa",
            bg="#0a1220"
        ).pack(pady=(0, 24))

        tk.Label(
            frame,
            text="Professional fully drawn animated puzzle game\nNo PNGs • No external images • Pure Canvas visuals",
            font=("Segoe UI", 15),
            fg="#b6c2d1",
            bg="#0a1220",
            justify="center"
        ).pack(pady=10)

        tk.Button(
            frame,
            text="Start Game",
            font=("Segoe UI", 15, "bold"),
            width=18,
            bg="#2563eb",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.build_game_screen
        ).pack(pady=28)

        tk.Label(
            frame,
            text=(
                "Goal: move the farmer, wolf, goat and cabbage safely across the river.\n"
                "Boat carries Farmer + one item only.\n"
                "Wolf cannot stay with Goat unattended.\n"
                "Goat cannot stay with Cabbage unattended."
            ),
            font=("Segoe UI", 13),
            fg="#dce5ee",
            bg="#0a1220",
            justify="center"
        ).pack(pady=12)

    def build_game_screen(self):
        self.clear_root()

        self.game.reset()
        self.animating = False
        self.demo_running = False
        self.elapsed_seconds = 0
        self.start_time = time.time()
        self.timer_running = True

        header = tk.Frame(self.root, bg="#101a2b", height=70)
        header.pack(fill="x")

        tk.Label(
            header,
            text="River Crossing Ultra Vector Edition",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="#101a2b"
        ).pack(side="left", padx=20, pady=16)

        self.mode_label = tk.Label(
            header,
            text="DAY MODE",
            font=("Segoe UI", 12, "bold"),
            fg="#facc15",
            bg="#101a2b"
        )
        self.mode_label.pack(side="right", padx=20)

        main = tk.Frame(self.root, bg="#0a1220")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        self.canvas = tk.Canvas(
            main,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#89d7ff",
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, padx=(0, 14))

        side = tk.Frame(main, bg="#121f33", width=380, height=self.canvas_height)
        side.grid(row=0, column=1, sticky="ns")
        side.grid_propagate(False)

        self.status_label = tk.Label(
            side,
            text="Choose a move.",
            font=("Segoe UI", 12, "bold"),
            fg="#4ade80",
            bg="#121f33",
            wraplength=320,
            justify="center"
        )
        self.status_label.pack(pady=(18, 10))

        stats = tk.Frame(side, bg="#121f33")
        stats.pack(pady=8)

        self.timer_label = self.make_stat(stats, "TIME", "00:00", 0, 0)
        self.moves_label = self.make_stat(stats, "MOVES", "0", 0, 1)
        self.score_label = self.make_stat(stats, "SCORE", "100", 1, 0)
        self.boat_side_label = self.make_stat(stats, "BOAT", "LEFT", 1, 1)

        button_frame = tk.Frame(side, bg="#121f33")
        button_frame.pack(pady=14)

        self.move_buttons = {}
        buttons = [
            ("Farmer Alone", "None", "#475569"),
            ("Take Wolf", "Wolf", "#6b7280"),
            ("Take Goat", "Goat", "#ca8a04"),
            ("Take Cabbage", "Cabbage", "#16a34a"),
        ]

        for text, value, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Segoe UI", 11, "bold"),
                width=22,
                bg=color,
                fg="white",
                relief="flat",
                cursor="hand2",
                command=lambda v=value: self.handle_move(v)
            )
            btn.pack(pady=6)
            self.move_buttons[value] = btn

        tools = tk.Frame(side, bg="#121f33")
        tools.pack(pady=8)

        tk.Button(tools, text="Hint", width=10, font=("Segoe UI", 10, "bold"),
                  bg="#2563eb", fg="white", relief="flat", command=self.show_hint).grid(row=0, column=0, padx=4, pady=4)

        tk.Button(tools, text="Auto Solve", width=10, font=("Segoe UI", 10, "bold"),
                  bg="#7c3aed", fg="white", relief="flat", command=self.start_demo).grid(row=0, column=1, padx=4, pady=4)

        tk.Button(tools, text="Day/Night", width=10, font=("Segoe UI", 10, "bold"),
                  bg="#0f766e", fg="white", relief="flat", command=self.toggle_day_night).grid(row=1, column=0, padx=4, pady=4)

        tk.Button(tools, text="Restart", width=10, font=("Segoe UI", 10, "bold"),
                  bg="#dc2626", fg="white", relief="flat", command=self.restart_game).grid(row=1, column=1, padx=4, pady=4)

        tk.Label(
            side, text="Move History",
            font=("Segoe UI", 14, "bold"),
            fg="white", bg="#121f33"
        ).pack(pady=(16, 6))

        self.history_box = tk.Text(
            side,
            width=36,
            height=18,
            font=("Consolas", 10),
            bg="#09111d",
            fg="white",
            relief="flat",
            state="disabled"
        )
        self.history_box.pack(pady=6)

        self.draw_scene()
        self.create_entities()
        self.refresh_positions()
        self.update_timer()
        self.animate_world()

    def make_stat(self, parent, title, value, row, col):
        card = tk.Frame(parent, bg="#09111d", highlightbackground="#243448", highlightthickness=1)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#09111d").pack(padx=24, pady=(8, 2))
        val = tk.Label(card, text=value, font=("Segoe UI", 14, "bold"), fg="white", bg="#09111d")
        val.pack(padx=24, pady=(0, 8))
        return val

    # =========================================================
    # DRAW SCENE
    # =========================================================
    def draw_scene(self):
        self.canvas.delete("all")
        self.entities = {}
        self.overlay_items = []

        if self.day_mode:
            self.draw_day_scene()
        else:
            self.draw_night_scene()

        self.draw_boat()

    def draw_day_scene(self):
        self.canvas.create_rectangle(0, 0, self.canvas_width, 165, fill="#caecff", outline="")
        self.canvas.create_oval(70, 30, 145, 105, fill="#ffd54f", outline="")
        self.canvas.create_rectangle(180, 130, 800, self.canvas_height, fill="#36aef7", outline="")
        self.canvas.create_rectangle(0, 130, 180, self.canvas_height, fill="#79c85b", outline="")
        self.canvas.create_rectangle(800, 130, self.canvas_width, self.canvas_height, fill="#79c85b", outline="")
        self.canvas.create_text(90, 95, text="LEFT BANK", font=("Segoe UI", 16, "bold"))
        self.canvas.create_text(890, 95, text="RIGHT BANK", font=("Segoe UI", 16, "bold"))

        self.draw_cloud(220, 45)
        self.draw_cloud(490, 28)
        self.draw_cloud(760, 48)
        self.draw_waves("#dff6ff")
        self.draw_grass_details()

    def draw_night_scene(self):
        self.canvas.create_rectangle(0, 0, self.canvas_width, 165, fill="#0f172a", outline="")
        self.canvas.create_oval(75, 35, 135, 95, fill="#e5e7eb", outline="")
        self.canvas.create_rectangle(180, 130, 800, self.canvas_height, fill="#1d4ed8", outline="")
        self.canvas.create_rectangle(0, 130, 180, self.canvas_height, fill="#3f6212", outline="")
        self.canvas.create_rectangle(800, 130, self.canvas_width, self.canvas_height, fill="#3f6212", outline="")
        self.canvas.create_text(90, 95, text="LEFT BANK", font=("Segoe UI", 16, "bold"), fill="white")
        self.canvas.create_text(890, 95, text="RIGHT BANK", font=("Segoe UI", 16, "bold"), fill="white")

        for i in range(34):
            x = 140 + (i * 29) % self.canvas_width
            y = 18 + (i * 19) % 115
            size = 10 if i % 3 else 12
            self.canvas.create_text(x, y, text="•", fill="white", font=("Arial", size))

        self.draw_waves("#a7d8ff")
        self.draw_grass_details(night=True)

    def draw_cloud(self, x, y):
        self.canvas.create_oval(x, y, x + 58, y + 36, fill="white", outline="")
        self.canvas.create_oval(x + 24, y - 12, x + 90, y + 30, fill="white", outline="")
        self.canvas.create_oval(x + 56, y, x + 115, y + 36, fill="white", outline="")

    def draw_waves(self, color):
        for y in range(165, 660, 30):
            shift = (self.wave_phase + y // 9) % 42
            for x in range(210, 770, 40):
                self.canvas.create_arc(
                    x + shift, y, x + shift + 24, y + 10,
                    start=0, extent=180, style="arc",
                    outline=color, width=2
                )

    def draw_grass_details(self, night=False):
        color = "#467d2e" if not night else "#35581f"
        for x in range(15, 170, 18):
            self.canvas.create_line(x, 645, x + 4, 630, fill=color, width=2)
            self.canvas.create_line(x + 8, 645, x + 4, 627, fill=color, width=2)

        for x in range(815, 965, 18):
            self.canvas.create_line(x, 645, x + 4, 630, fill=color, width=2)
            self.canvas.create_line(x + 8, 645, x + 4, 627, fill=color, width=2)

    def draw_boat(self):
        boat_x = self.boat_left_x if self.game.farmer_side == "left" else self.boat_right_x
        bob = math.sin(self.boat_bob_phase) * 3
        y = self.boat_y + bob

        self.boat_shadow = self.canvas.create_oval(
            boat_x + 12, y + 34, boat_x + 110, y + 48,
            fill="#237db6", outline=""
        )

        self.boat = self.canvas.create_polygon(
            boat_x, y,
            boat_x + 130, y,
            boat_x + 104, y + 40,
            boat_x + 20, y + 40,
            fill="#7c4a28",
            outline="#3a2416",
            width=2
        )
        self.boat_mast = self.canvas.create_line(
            boat_x + 56, y, boat_x + 56, y - 62,
            fill="#5b3820", width=4
        )
        self.boat_sail = self.canvas.create_polygon(
            boat_x + 58, y - 62,
            boat_x + 58, y - 10,
            boat_x + 102, y - 34,
            fill="#fff7d6",
            outline="#d9cda7", width=2
        )

    # =========================================================
    # ENTITY CREATION
    # =========================================================
    def create_entities(self):
        self.entities["Farmer"] = self.create_farmer(0, 0)
        self.entities["Wolf"] = self.create_wolf(0, 0)
        self.entities["Goat"] = self.create_goat(0, 0)
        self.entities["Cabbage"] = self.create_cabbage(0, 0)

    def create_farmer(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 12, y, x + 38, y + 26, fill="#f2c48d", outline="black", width=2))
        ids.append(self.canvas.create_arc(x + 8, y - 4, x + 42, y + 18, start=0, extent=180, fill="#8b5a2b", outline="black"))
        ids.append(self.canvas.create_rectangle(x + 16, y + 26, x + 34, y + 62, fill="#2d67b1", outline="black", width=2))
        ids.append(self.canvas.create_line(x + 24, y + 62, x + 14, y + 90, width=4))
        ids.append(self.canvas.create_line(x + 26, y + 62, x + 38, y + 90, width=4))
        ids.append(self.canvas.create_line(x + 16, y + 40, x + 0, y + 62, width=4))
        ids.append(self.canvas.create_line(x + 34, y + 40, x + 48, y + 58, width=4))
        ids.append(self.canvas.create_line(x + 48, y + 58, x + 57, y + 84, width=3, fill="#7b4b2a"))
        ids.append(self.canvas.create_text(x + 28, y + 104, text="Farmer", font=("Segoe UI", 10, "bold")))
        return ids

    def create_wolf(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 10, y + 24, x + 86, y + 66, fill="#7a8691", outline="black", width=2))
        ids.append(self.canvas.create_oval(x + 64, y + 10, x + 98, y + 38, fill="#7a8691", outline="black", width=2))
        ids.append(self.canvas.create_polygon(x + 68, y + 12, x + 74, y - 4, x + 80, y + 12, fill="#7a8691", outline="black"))
        ids.append(self.canvas.create_polygon(x + 82, y + 12, x + 88, y - 4, x + 94, y + 12, fill="#7a8691", outline="black"))
        ids.append(self.canvas.create_oval(x + 86, y + 22, x + 90, y + 26, fill="black", outline=""))
        ids.append(self.canvas.create_line(x + 16, y + 66, x + 16, y + 90, width=4))
        ids.append(self.canvas.create_line(x + 32, y + 66, x + 32, y + 90, width=4))
        ids.append(self.canvas.create_line(x + 56, y + 66, x + 56, y + 90, width=4))
        ids.append(self.canvas.create_line(x + 72, y + 66, x + 72, y + 90, width=4))
        ids.append(self.canvas.create_line(x + 10, y + 35, x - 12, y + 20, width=4))
        ids.append(self.canvas.create_text(x + 48, y + 106, text="Wolf", font=("Segoe UI", 10, "bold")))
        return ids

    def create_goat(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 12, y + 24, x + 82, y + 64, fill="#f1dfc0", outline="black", width=2))
        ids.append(self.canvas.create_oval(x + 62, y + 10, x + 96, y + 40, fill="#f1dfc0", outline="black", width=2))
        ids.append(self.canvas.create_line(x + 68, y + 10, x + 60, y - 6, width=3))
        ids.append(self.canvas.create_line(x + 84, y + 10, x + 92, y - 6, width=3))
        ids.append(self.canvas.create_oval(x + 82, y + 22, x + 86, y + 26, fill="black", outline=""))
        ids.append(self.canvas.create_line(x + 20, y + 64, x + 20, y + 92, width=4))
        ids.append(self.canvas.create_line(x + 36, y + 64, x + 36, y + 92, width=4))
        ids.append(self.canvas.create_line(x + 54, y + 64, x + 54, y + 92, width=4))
        ids.append(self.canvas.create_line(x + 70, y + 64, x + 70, y + 92, width=4))
        ids.append(self.canvas.create_line(x + 12, y + 36, x - 8, y + 24, width=3))
        ids.append(self.canvas.create_text(x + 48, y + 108, text="Goat", font=("Segoe UI", 10, "bold")))
        return ids

    def create_cabbage(self, x, y):
        ids = []
        ids.append(self.canvas.create_oval(x + 10, y + 10, x + 78, y + 78, fill="#36b44a", outline="black", width=2))
        ids.append(self.canvas.create_oval(x + 18, y + 18, x + 70, y + 70, fill="#67d971", outline=""))
        ids.append(self.canvas.create_arc(x + 20, y + 20, x + 68, y + 68, start=20, extent=120, style="arc", width=2))
        ids.append(self.canvas.create_arc(x + 20, y + 20, x + 68, y + 68, start=165, extent=110, style="arc", width=2))
        ids.append(self.canvas.create_arc(x + 24, y + 24, x + 64, y + 64, start=70, extent=110, style="arc", width=2))
        ids.append(self.canvas.create_text(x + 44, y + 100, text="Cabbage", font=("Segoe UI", 10, "bold")))
        return ids

    # =========================================================
    # ENTITY MOVEMENT HELPERS
    # =========================================================
    def entity_ids(self, name):
        return self.entities[name]

    def entity_bbox(self, name):
        return self.canvas.bbox(self.entity_ids(name)[0])

    def entity_top_left(self, name):
        bbox = self.entity_bbox(name)
        return bbox[0], bbox[1]

    def move_entity_by(self, name, dx, dy):
        for item in self.entity_ids(name):
            self.canvas.move(item, dx, dy)

    def move_entity_to(self, name, x, y):
        cx, cy = self.entity_top_left(name)
        self.move_entity_by(name, x - cx, y - cy)

    # =========================================================
    # REFRESH / HUD
    # =========================================================
    def refresh_positions(self):
        self.draw_scene()
        self.create_entities()

        for item in ["Farmer", "Wolf", "Goat", "Cabbage"]:
            if item in self.game.left:
                self.move_entity_to(item, self.left_x, self.bank_y[item])
            elif item in self.game.right:
                self.move_entity_to(item, self.right_x, self.bank_y[item])

        self.update_history()
        self.update_stats()
        self.update_buttons()

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
        self.timer_label.config(text=self.format_time(self.elapsed_seconds))
        self.moves_label.config(text=str(self.game.move_count))
        self.score_label.config(text=str(self.game.score))
        self.boat_side_label.config(text=self.game.farmer_side.upper())
        self.mode_label.config(text="DAY MODE" if self.day_mode else "NIGHT MODE")

    def update_buttons(self):
        possible = self.game.get_possible_moves()
        for item, btn in self.move_buttons.items():
            if self.animating:
                btn.config(state="disabled")
            else:
                btn.config(state="normal" if item in possible else "disabled")

    def update_timer(self):
        if self.timer_running and self.start_time is not None:
            self.elapsed_seconds = int(time.time() - self.start_time)
            if hasattr(self, "timer_label"):
                self.timer_label.config(text=self.format_time(self.elapsed_seconds))
        self.root.after(1000, self.update_timer)

    def format_time(self, sec):
        return f"{sec // 60:02d}:{sec % 60:02d}"

    # =========================================================
    # UI ACTIONS
    # =========================================================
    def show_hint(self):
        self.status_label.config(text=f"Hint: {self.game.next_hint()}", fg="#facc15")

    def toggle_day_night(self):
        if self.animating:
            return
        self.day_mode = not self.day_mode
        self.refresh_positions()

    def restart_game(self):
        if self.animating:
            return
        self.build_game_screen()

    # =========================================================
    # PLAYER MOVE FLOW
    # =========================================================
    def handle_move(self, item):
        if self.animating:
            return

        self.trip_side_before = self.game.farmer_side

        success, msg = self.game.move(item)
        if not success:
            self.status_label.config(text=msg, fg="#ef4444")
            return

        self.trip_item = None if item == "None" else item
        self.status_label.config(text=msg, fg="#60a5fa")
        self.animating = True
        self.update_buttons()

        self.walk_to_boat(item)

    def walk_to_boat(self, item):
        side = self.trip_side_before
        farmer_target = self.left_edge_x if side == "left" else self.right_edge_x - 20
        item_target = self.left_edge_x - 25 if side == "left" else self.right_edge_x - 45

        def step():
            done_farmer = self.step_towards_x("Farmer", farmer_target, 5)
            done_item = True

            if item != "None":
                done_item = self.step_towards_x(item, item_target, 5)

            if done_farmer and done_item:
                self.board_boat(item)
            else:
                self.root.after(20, step)

        step()

    def board_boat(self, item):
        start_x = self.boat_left_x if self.trip_side_before == "left" else self.boat_right_x
        self.move_entity_to("Farmer", start_x + 16, self.boat_y - 45)

        if item != "None":
            self.move_entity_to(item, start_x + 72, self.boat_y - 35)

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
                self.finish_crossing()
                return

            dx = 6 if diff > 0 else -6
            current_x += dx
            self.move_boat_group(dx)
            self.root.after(20, step)

        step()

    def move_boat_group(self, dx):
        for boat_part in [self.boat_shadow, self.boat, self.boat_mast, self.boat_sail]:
            self.canvas.move(boat_part, dx, 0)

        self.move_entity_by("Farmer", dx, 0)
        if self.trip_item:
            self.move_entity_by(self.trip_item, dx, 0)

    def finish_crossing(self):
        valid, reason = self.game.is_valid()
        self.refresh_positions()

        if not valid:
            self.status_label.config(text=reason, fg="#ef4444")
            self.animating = False
            self.update_buttons()
            messagebox.showerror("Game Over", reason)
            return

        if self.game.is_won():
            self.timer_running = False
            self.animating = False
            self.show_win_overlay()
            return

        self.status_label.config(text="Choose your next move.", fg="#4ade80")
        self.animating = False
        self.update_buttons()

    def step_towards_x(self, name, target_x, speed):
        x, _ = self.entity_top_left(name)
        diff = target_x - x
        if abs(diff) <= speed:
            self.move_entity_by(name, diff, 0)
            return True

        dx = speed if diff > 0 else -speed
        self.move_entity_by(name, dx, 0)

        # small walk bounce
        bounce = math.sin((self.idle_phase + x) * 0.15) * 0.6
        self.move_entity_by(name, 0, bounce)
        return False

    # =========================================================
    # AUTO SOLVE
    # =========================================================
    def start_demo(self):
        if self.animating:
            return

        self.build_game_screen()
        self.demo_running = True
        self.status_label.config(text="Auto solve started.", fg="#c084fc")
        self.root.after(700, self.perform_demo_step)

    def perform_demo_step(self):
        if not self.demo_running or self.animating:
            return

        index = len(self.game.history)
        if index >= len(self.game.solution_steps):
            self.demo_running = False
            return

        next_item = self.game.solution_steps[index]
        self.handle_move(next_item)

        if self.demo_running:
            self.root.after(1900, self.perform_demo_step)

    # =========================================================
    # WORLD ANIMATION
    # =========================================================
    def animate_world(self):
        if not hasattr(self, "canvas"):
            self.root.after(150, self.animate_world)
            return

        self.wave_phase = (self.wave_phase + 3) % 40
        self.boat_bob_phase += 0.15
        self.idle_phase += 0.2

        if not self.animating:
            left_set = set(self.game.left)
            right_set = set(self.game.right)

            self.draw_scene()
            self.create_entities()

            for item in ["Farmer", "Wolf", "Goat", "Cabbage"]:
                base_y = self.bank_y[item]

                idle_offset_y = 0
                idle_offset_x = 0

                if item == "Farmer":
                    idle_offset_y = math.sin(self.idle_phase * 1.8) * 1.5
                elif item == "Wolf":
                    idle_offset_x = math.sin(self.idle_phase * 1.5) * 1.5
                    idle_offset_y = math.cos(self.idle_phase * 1.2) * 1.0
                elif item == "Goat":
                    idle_offset_y = math.sin(self.idle_phase * 2.2) * 2.0
                elif item == "Cabbage":
                    idle_offset_y = math.sin(self.idle_phase) * 0.8

                if item in left_set:
                    self.move_entity_to(item, self.left_x + idle_offset_x, base_y + idle_offset_y)
                elif item in right_set:
                    self.move_entity_to(item, self.right_x + idle_offset_x, base_y + idle_offset_y)

            self.update_history()
            self.update_stats()
            self.update_buttons()

        self.root.after(140, self.animate_world)

    # =========================================================
    # WIN OVERLAY
    # =========================================================
    def show_win_overlay(self):
        final_score = self.game.final_score(self.elapsed_seconds)

        overlay = self.canvas.create_rectangle(
            110, 120, 870, 560,
            fill="#06111dcc", outline="#60a5fa", width=3
        )
        title = self.canvas.create_text(
            490, 200,
            text="PUZZLE SOLVED!",
            font=("Segoe UI", 30, "bold"),
            fill="#4ade80"
        )
        t1 = self.canvas.create_text(
            490, 280,
            text=f"Time: {self.format_time(self.elapsed_seconds)}",
            font=("Segoe UI", 18, "bold"),
            fill="white"
        )
        t2 = self.canvas.create_text(
            490, 325,
            text=f"Moves: {self.game.move_count}",
            font=("Segoe UI", 18, "bold"),
            fill="white"
        )
        t3 = self.canvas.create_text(
            490, 370,
            text=f"Final Score: {final_score}",
            font=("Segoe UI", 22, "bold"),
            fill="#facc15"
        )

        self.overlay_items = [overlay, title, t1, t2, t3]

        restart_btn = tk.Button(
            self.root,
            text="Play Again",
            font=("Segoe UI", 12, "bold"),
            bg="#2563eb",
            fg="white",
            relief="flat",
            command=self.build_game_screen
        )
        start_btn = tk.Button(
            self.root,
            text="Back to Start",
            font=("Segoe UI", 12, "bold"),
            bg="#475569",
            fg="white",
            relief="flat",
            command=self.build_start_screen
        )

        self.overlay_items.append(self.canvas.create_window(430, 450, window=restart_btn))
        self.overlay_items.append(self.canvas.create_window(550, 450, window=start_btn))


if __name__ == "__main__":
    root = tk.Tk()
    app = RiverCrossingUltraVectorGUI(root)
    root.mainloop()