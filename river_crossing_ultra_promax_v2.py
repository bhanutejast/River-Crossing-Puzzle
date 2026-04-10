import tkinter as tk
from tkinter import messagebox
import math


class RiverCrossingEngine:
    def __init__(self):
        self.solution = ["Goat", "None", "Wolf", "Goat", "Cabbage", "None", "Goat"]
        self.reset()

    def reset(self):
        self.left = {"Farmer", "Wolf", "Goat", "Cabbage"}
        self.right = set()
        self.farmer_side = "left"
        self.history = []
        self.moves = 0

    def current_bank(self):
        return self.left if self.farmer_side == "left" else self.right

    def other_bank(self):
        return self.right if self.farmer_side == "left" else self.left

    def possible_moves(self):
        bank = self.current_bank()
        return ["None"] + sorted(x for x in bank if x != "Farmer")

    def move(self, item):
        bank = self.current_bank()
        other = self.other_bank()
        if item != "None" and item not in bank:
            return False, f"{item} is not on the same side as the farmer."

        bank.remove("Farmer")
        other.add("Farmer")

        if item != "None":
            bank.remove(item)
            other.add(item)
            self.history.append(f"Farmer takes {item}")
        else:
            self.history.append("Farmer goes alone")

        self.farmer_side = "right" if self.farmer_side == "left" else "left"
        self.moves += 1
        return True, self.history[-1]

    def valid_state(self):
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

    def won(self):
        return self.right == {"Farmer", "Wolf", "Goat", "Cabbage"}


class RiverCrossingUltraPromax:
    def __init__(self, root):
        self.root = root
        self.root.title("River Crossing Ultra Promax")
        self.root.geometry("1500x920")
        self.root.configure(bg="#07131f")
        self.root.resizable(False, False)

        self.game = RiverCrossingEngine()
        self.animating = False
        self.auto_mode = False
        self.day = True
        self.started = False
        self.phase = 0.0
        self.wave = 0.0
        self.bob = 0.0
        self.spark = 0.0
        self.trip_item = None
        self.boat_x = 310
        self.start_ms = 0

        self.cw = 1100
        self.ch = 780

        self.left_bank_x = 85
        self.right_bank_x = 900
        self.base_y = {
            "Farmer": 165,
            "Wolf": 320,
            "Goat": 475,
            "Cabbage": 625,
        }

        self.boat_left_x = 310
        self.boat_right_x = 635
        self.boat_y = 520

        self.items = {}
        self.item_defs = {}
        self.overlay_items = []
        self.stars = []
        self.ripples = []

        self.build_ui()
        self.draw_scene()
        self.show_start_screen()
        self.animation_loop()

    def build_ui(self):
        top = tk.Frame(self.root, bg="#07131f")
        top.pack(fill="x", padx=14, pady=(10, 6))

        tk.Label(top, text="RIVER CROSSING ULTRA PROMAX", font=("Segoe UI", 30, "bold"), bg="#07131f", fg="#f6fbff").pack()
        tk.Label(top, text="Realistic vector-style characters • smooth corrected boat motion • hint • auto solve • day/night", font=("Segoe UI", 12, "bold"), bg="#07131f", fg="#98bcff").pack(pady=(4, 0))

        wrap = tk.Frame(self.root, bg="#07131f")
        wrap.pack(fill="both", expand=True, padx=14, pady=10)

        self.canvas = tk.Canvas(wrap, width=self.cw, height=self.ch, bg="#8fd8ff", highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=(0, 14), sticky="nsew")

        side = tk.Frame(wrap, bg="#11233f", width=340, height=self.ch)
        side.grid(row=0, column=1, sticky="ns")
        side.grid_propagate(False)

        tk.Label(side, text="Control Panel", font=("Segoe UI", 21, "bold"), bg="#11233f", fg="white").pack(pady=(16, 8))

        self.status = tk.Label(side, text="Press START GAME", font=("Segoe UI", 12, "bold"), bg="#11233f", fg="#8dff9a", wraplength=290, justify="center", height=3)
        self.status.pack(pady=(2, 8))

        self.meta = tk.Label(side, text="Boat: LEFT | Moves: 0", font=("Segoe UI", 12, "bold"), bg="#11233f", fg="#ffd36c")
        self.meta.pack(pady=(0, 6))

        self.timer = tk.Label(side, text="Timer: 0.0 s", font=("Segoe UI", 12, "bold"), bg="#11233f", fg="#8cdcff")
        self.timer.pack(pady=(0, 12))

        self.move_buttons = {}
        for text, val, col in [
            ("Farmer Alone", "None", "#50647d"),
            ("Take Wolf", "Wolf", "#677787"),
            ("Take Goat", "Goat", "#bd8e16"),
            ("Take Cabbage", "Cabbage", "#227748"),
        ]:
            b = tk.Button(side, text=text, font=("Segoe UI", 12, "bold"), width=22, bg=col, fg="white", activebackground=col, activeforeground="white", relief="flat", bd=0, cursor="hand2", command=lambda x=val: self.handle_move(x))
            b.pack(pady=7)
            self.move_buttons[val] = b

        row1 = tk.Frame(side, bg="#11233f")
        row1.pack(pady=(16, 6))
        tk.Button(row1, text="START GAME", font=("Segoe UI", 11, "bold"), width=13, bg="#00a56b", fg="white", relief="flat", bd=0, command=self.start_game, cursor="hand2").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(row1, text="RESTART", font=("Segoe UI", 11, "bold"), width=13, bg="#d64545", fg="white", relief="flat", bd=0, command=self.restart_game, cursor="hand2").grid(row=0, column=1, padx=5, pady=5)

        row2 = tk.Frame(side, bg="#11233f")
        row2.pack(pady=(2, 6))
        tk.Button(row2, text="HINT", font=("Segoe UI", 11, "bold"), width=13, bg="#8d46ff", fg="white", relief="flat", bd=0, command=self.show_hint, cursor="hand2").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(row2, text="AUTO SOLVE", font=("Segoe UI", 11, "bold"), width=13, bg="#ff7c1f", fg="white", relief="flat", bd=0, command=self.auto_solve, cursor="hand2").grid(row=0, column=1, padx=5, pady=5)

        row3 = tk.Frame(side, bg="#11233f")
        row3.pack(pady=(2, 10))
        tk.Button(row3, text="DAY / NIGHT", font=("Segoe UI", 11, "bold"), width=13, bg="#2f55a4", fg="white", relief="flat", bd=0, command=self.toggle_mode, cursor="hand2").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(row3, text="RULES", font=("Segoe UI", 11, "bold"), width=13, bg="#228fff", fg="white", relief="flat", bd=0, command=self.show_rules, cursor="hand2").grid(row=0, column=1, padx=5, pady=5)

        tk.Label(side, text="Move History", font=("Segoe UI", 15, "bold"), bg="#11233f", fg="white").pack(pady=(8, 6))
        self.history_box = tk.Text(side, width=35, height=19, font=("Consolas", 10), bg="#081628", fg="#e9f3ff", relief="flat")
        self.history_box.pack(pady=(0, 10))
        self.history_box.config(state="disabled")

        tk.Label(side, text="Renamed file:\nriver_crossing_ultra_promax_realistic.py", font=("Segoe UI", 11, "bold"), bg="#11233f", fg="#b8c9ff").pack(pady=(8, 0))

    def set_status(self, text, color="#8dff9a"):
        self.status.config(text=text, fg=color)

    def start_game(self):
        self.started = True
        self.auto_mode = False
        self.game.reset()
        self.boat_x = self.boat_left_x
        self.start_ms = self.root.tk.call("clock", "milliseconds")
        self.set_status("Game started. Choose a move.")
        self.draw_scene()
        self.refresh_positions()

    def restart_game(self):
        if self.animating:
            return
        self.start_game()

    def toggle_mode(self):
        self.day = not self.day
        self.draw_scene()
        if self.started:
            self.refresh_positions()
        self.set_status("Visual mode changed.", "#8cdcff")

    def show_rules(self):
        messagebox.showinfo("Rules", "Boat can carry the Farmer and only one item.\nNever leave Wolf with Goat alone.\nNever leave Goat with Cabbage alone.\nTake all safely to the right bank.")

    def show_hint(self):
        if not self.started or self.animating:
            return
        i = len(self.game.history)
        if i < len(self.game.solution):
            m = self.game.solution[i]
            self.set_status("Hint: Farmer goes alone." if m == "None" else f"Hint: Take {m}.", "#d5b0ff")

    def auto_solve(self):
        if not self.started or self.animating:
            return
        self.auto_mode = True
        self.auto_step()

    def auto_step(self):
        if not self.auto_mode or self.animating or self.game.won():
            return
        i = len(self.game.history)
        if i < len(self.game.solution):
            self.handle_move(self.game.solution[i], auto=True)
            self.root.after(900, self.auto_step)

    def update_controls(self):
        possible = self.game.possible_moves() if self.started else []
        for k, b in self.move_buttons.items():
            if self.animating:
                b.config(state="disabled")
            else:
                b.config(state="normal" if k in possible else "disabled")

    def draw_gradient(self, x1, y1, x2, y2, c1, c2, steps=40):
        r1, g1, b1 = self.hex_to_rgb(c1)
        r2, g2, b2 = self.hex_to_rgb(c2)
        h = (y2 - y1) / steps
        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            self.canvas.create_rectangle(x1, y1 + i * h, x2, y1 + (i + 1) * h + 1, fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

    def hex_to_rgb(self, h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def draw_scene(self):
        self.canvas.delete("all")
        self.overlay_items = []
        self.stars = []
        self.ripples = []

        if self.day:
            sky1, sky2 = "#73cfff", "#e6f8ff"
            river1, river2 = "#2493d8", "#1e7fc0"
            bank1, bank2 = "#67bf4e", "#83d66c"
        else:
            sky1, sky2 = "#06132b", "#17365f"
            river1, river2 = "#144f82", "#0f3d65"
            bank1, bank2 = "#355f37", "#4a7a4f"

        self.draw_gradient(0, 0, self.cw, 190, sky1, sky2)

        if self.day:
            self.canvas.create_oval(65, 45, 160, 140, fill="#ffd85f", outline="")
            for i in range(5):
                self.canvas.create_oval(60 - i * 6, 40 - i * 6, 165 + i * 6, 145 + i * 6, outline="#ffe99c")
        else:
            self.canvas.create_oval(82, 48, 150, 116, fill="#f4f7ff", outline="")
            for x, y in [(240, 60), (340, 120), (460, 75), (590, 105), (760, 65), (915, 118), (1020, 70)]:
                self.stars.append(self.canvas.create_text(x, y, text="✦", font=("Segoe UI", 16, "bold"), fill="#ffffff"))

        for x in range(20, 230, 60):
            self.canvas.create_oval(x, 120, x + 120, 180, fill="#eef8ff", outline="")
        for x in range(840, 1110, 60):
            self.canvas.create_oval(x, 125, x + 120, 183, fill="#eef8ff", outline="")

        self.draw_gradient(0, 190, 210, 760, bank1, bank2)
        self.draw_gradient(890, 190, self.cw, 760, bank1, bank2)
        self.draw_gradient(210, 190, 890, 760, river1, river2)

        self.canvas.create_polygon(0, 195, 220, 140, 300, 200, 0, 235, fill=bank2, outline="")
        self.canvas.create_polygon(820, 195, self.cw, 145, self.cw, 245, 890, 220, fill=bank2, outline="")

        self.canvas.create_text(108, 82, text="LEFT BANK", font=("Segoe UI", 18, "bold"), fill="#10233d")
        self.canvas.create_text(990, 82, text="RIGHT BANK", font=("Segoe UI", 18, "bold"), fill="#10233d")

        for i in range(13):
            y = 230 + i * 37
            self.ripples.append((240 + i * 40, y))

        self.draw_boat(self.boat_x)
        self.create_character_art()

    def draw_boat(self, x):
        y = self.boat_y + math.sin(self.bob) * 3
        self.boat_group = []
        shadow = self.canvas.create_oval(x + 18, y + 42, x + 158, y + 60, fill="#0e4b74", outline="")
        hull = self.canvas.create_polygon(x, y, x + 176, y, x + 150, y + 46, x + 25, y + 46, fill="#5a2f14", outline="#1f120a", width=3)
        rim = self.canvas.create_polygon(x + 20, y + 5, x + 155, y + 5, x + 140, y + 19, x + 35, y + 19, fill="#8a5c34", outline="")
        mast = self.canvas.create_line(x + 88, y + 3, x + 88, y - 90, fill="#f2f2f2", width=3)
        sail = self.canvas.create_polygon(x + 88, y - 88, x + 138, y - 58, x + 88, y - 28, fill="#fbf6ea", outline="#bda98f", width=2)
        self.boat_group.extend([shadow, hull, rim, mast, sail])

    def create_character_art(self):
        self.items = {}
        self.item_defs = {}
        self.make_farmer("Farmer")
        self.make_wolf("Wolf")
        self.make_goat("Goat")
        self.make_cabbage("Cabbage")

    def make_farmer(self, name):
        g = []
        p = self.phase
        arm = math.sin(p * 3.0) * 4
        leg = math.sin(p * 3.0) * 3
        body = math.sin(p * 1.8) * 1.5
        g.append(self.canvas.create_oval(28, 5 + body, 72, 49 + body, fill="#e7c08d", outline="#241710", width=2))
        g.append(self.canvas.create_arc(23, -3 + body, 77, 30 + body, start=0, extent=180, fill="#6f4423", outline="#6f4423"))
        g.append(self.canvas.create_oval(42, 21 + body, 48, 27 + body, fill="#241710", outline=""))
        g.append(self.canvas.create_oval(52, 21 + body, 58, 27 + body, fill="#241710", outline=""))
        g.append(self.canvas.create_arc(42, 28 + body, 58, 36 + body, start=200, extent=140, style="arc", outline="#7a3321", width=2))
        g.append(self.canvas.create_rectangle(30, 49 + body, 70, 108 + body, fill="#315db5", outline="#1d2d55", width=2))
        g.append(self.canvas.create_polygon(30, 57 + body, 20, 86 + arm, 27, 89 + arm, 40, 65 + body, fill="#e7c08d", outline="#241710"))
        g.append(self.canvas.create_polygon(70, 57 + body, 82, 85 - arm, 75, 89 - arm, 60, 66 + body, fill="#e7c08d", outline="#241710"))
        g.append(self.canvas.create_polygon(40, 108 + body, 29, 146 + leg, 36, 149 + leg, 49, 112 + body, fill="#202938", outline="#151922"))
        g.append(self.canvas.create_polygon(59, 108 + body, 70, 146 - leg, 63, 149 - leg, 51, 112 + body, fill="#202938", outline="#151922"))
        g.append(self.canvas.create_text(50, 168, text="Farmer", font=("Segoe UI", 11, "bold"), fill="white"))
        self.items[name] = g

    def make_wolf(self, name):
        g = []
        p = self.phase
        tail = math.sin(p * 3.4) * 6
        chest = math.sin(p * 2.0) * 1.5
        g.append(self.canvas.create_polygon(16, 90, 24, 60, 54, 40 + chest, 108, 42, 130, 62, 128, 92, 103, 112, 42, 112, fill="#77818a", outline="#23282d", width=2, smooth=True))
        g.append(self.canvas.create_polygon(103, 50, 136, 30, 154, 40, 150, 69, 124, 82, 102, 74, fill="#86909a", outline="#23282d", width=2, smooth=True))
        g.append(self.canvas.create_polygon(120, 34, 129, 10, 138, 34, fill="#7a848d", outline="#23282d", width=2))
        g.append(self.canvas.create_polygon(136, 36, 146, 12, 153, 38, fill="#7a848d", outline="#23282d", width=2))
        g.append(self.canvas.create_line(18, 78, 2, 57 + tail, fill="#6c757d", width=5, smooth=True))
        for x in [36, 64, 92, 116]:
            g.append(self.canvas.create_line(x, 108, x - 2, 148, fill="#1f252b", width=5))
        g.append(self.canvas.create_oval(134, 47, 140, 53, fill="#111", outline=""))
        g.append(self.canvas.create_polygon(149, 55, 160, 59, 149, 63, fill="#40474e", outline="#23282d"))
        g.append(self.canvas.create_text(78, 168, text="Wolf", font=("Segoe UI", 11, "bold"), fill="white"))
        self.items[name] = g

    def make_goat(self, name):
        g = []
        p = self.phase
        hop = math.sin(p * 3.8) * 2
        g.append(self.canvas.create_polygon(20, 92 + hop, 30, 56 + hop, 62, 42 + hop, 113, 44 + hop, 138, 66 + hop, 132, 98 + hop, 103, 114 + hop, 45, 114 + hop, fill="#ecdfc4", outline="#4a3d2d", width=2, smooth=True))
        g.append(self.canvas.create_polygon(100, 52 + hop, 128, 33 + hop, 146, 42 + hop, 144, 69 + hop, 121, 81 + hop, 100, 74 + hop, fill="#efe4cb", outline="#4a3d2d", width=2, smooth=True))
        g.append(self.canvas.create_line(111, 36 + hop, 104, 15 + hop, fill="#4a3d2d", width=3))
        g.append(self.canvas.create_line(130, 38 + hop, 138, 16 + hop, fill="#4a3d2d", width=3))
        for x in [42, 67, 91, 112]:
            g.append(self.canvas.create_line(x, 110 + hop, x - 1, 148 + hop, fill="#4a3d2d", width=4))
        g.append(self.canvas.create_oval(129, 50 + hop, 135, 56 + hop, fill="#111", outline=""))
        g.append(self.canvas.create_text(79, 168, text="Goat", font=("Segoe UI", 11, "bold"), fill="white"))
        self.items[name] = g

    def make_cabbage(self, name):
        g = []
        p = self.phase
        pulse = math.sin(p * 2.0) * 2
        g.append(self.canvas.create_oval(24 - pulse, 28 - pulse, 126 + pulse, 128 + pulse, fill="#3ba744", outline="#184f1f", width=3))
        g.append(self.canvas.create_oval(39, 43, 111, 115, fill="#67d069", outline=""))
        g.append(self.canvas.create_arc(34, 38, 118, 120, start=20, extent=290, style="arc", outline="#2a7b32", width=2))
        g.append(self.canvas.create_arc(46, 49, 105, 107, start=20, extent=300, style="arc", outline="#2a7b32", width=2))
        g.append(self.canvas.create_arc(57, 61, 94, 95, start=20, extent=300, style="arc", outline="#2a7b32", width=2))
        g.append(self.canvas.create_text(75, 168, text="Cabbage", font=("Segoe UI", 11, "bold"), fill="white"))
        self.items[name] = g

    def group_bbox(self, name):
        boxes = [self.canvas.bbox(i) for i in self.items[name] if self.canvas.bbox(i)]
        x1 = min(b[0] for b in boxes)
        y1 = min(b[1] for b in boxes)
        x2 = max(b[2] for b in boxes)
        y2 = max(b[3] for b in boxes)
        return x1, y1, x2, y2

    def place_item(self, name, x, y):
        bx1, by1, _, _ = self.group_bbox(name)
        dx = x - bx1
        dy = y - by1
        for item in self.items[name]:
            self.canvas.move(item, dx, dy)

    def refresh_positions(self):
        if not self.started:
            self.update_controls()
            return

        elapsed = max(0, self.root.tk.call("clock", "milliseconds") - self.start_ms) / 1000
        self.timer.config(text=f"Timer: {elapsed:.1f} s")
        self.meta.config(text=f"Boat: {self.game.farmer_side.upper()} | Moves: {self.game.moves}")

        for n in ["Farmer", "Wolf", "Goat", "Cabbage"]:
            if n in self.game.left:
                self.place_item(n, self.left_bank_x, self.base_y[n])
            else:
                self.place_item(n, self.right_bank_x, self.base_y[n])

        self.update_history()
        self.update_controls()

    def update_history(self):
        self.history_box.config(state="normal")
        self.history_box.delete("1.0", "end")
        if not self.game.history:
            self.history_box.insert("end", "No moves yet.\n")
        else:
            for i, m in enumerate(self.game.history, 1):
                self.history_box.insert("end", f"{i:02d}. {m}\n")
        self.history_box.config(state="disabled")

    def handle_move(self, item, auto=False):
        if not self.started or self.animating:
            return

        side_before = self.game.farmer_side
        ok, msg = self.game.move(item)
        if not ok:
            self.set_status(msg, "#ff8d8d")
            return

        self.animating = True
        self.trip_item = None if item == "None" else item
        self.set_status(msg, "#ffd36c" if auto else "#8dff9a")

        start_x = self.boat_left_x if side_before == "left" else self.boat_right_x
        end_x = self.boat_right_x if side_before == "left" else self.boat_left_x
        self.boat_x = start_x

        self.draw_scene()
        self.refresh_positions()
        self.place_item("Farmer", start_x + 34, self.boat_y - 122)
        if self.trip_item:
            self.place_item(self.trip_item, start_x + 92, self.boat_y - 122)
        self.animate_boat(end_x)

    def move_group(self, name, dx, dy):
        for i in self.items[name]:
            self.canvas.move(i, dx, dy)

    def animate_boat(self, target_x):
        diff = target_x - self.boat_x
        if abs(diff) <= 7:
            step = diff
        else:
            step = 7 if diff > 0 else -7

        self.boat_x += step
        for i in self.boat_group:
            self.canvas.move(i, step, 0)
        self.move_group("Farmer", step, 0)
        if self.trip_item:
            self.move_group(self.trip_item, step, 0)

        if abs(diff) <= 7:
            self.finish_move()
        else:
            self.root.after(16, lambda: self.animate_boat(target_x))

    def finish_move(self):
        self.draw_scene()
        self.refresh_positions()
        valid, reason = self.game.valid_state()
        self.animating = False

        if not valid:
            self.auto_mode = False
            self.set_status(reason, "#ff7e7e")
            self.show_game_over(reason)
            return

        if self.game.won():
            self.auto_mode = False
            self.set_status("Perfect. Puzzle solved.", "#8dff9a")
            self.show_win_screen()
            return

        self.update_controls()

    def clear_overlay(self):
        for i in self.overlay_items:
            self.canvas.delete(i)
        self.overlay_items = []

    def show_start_screen(self):
        self.clear_overlay()
        self.overlay_items.append(self.canvas.create_rectangle(0, 0, self.cw, self.ch, fill="#000000", stipple="gray50", outline=""))
        self.overlay_items.append(self.canvas.create_text(self.cw // 2, 220, text="RIVER CROSSING", font=("Segoe UI", 42, "bold"), fill="#ffffff"))
        self.overlay_items.append(self.canvas.create_text(self.cw // 2, 286, text="ULTRA PROMAX REALISTIC EDITION", font=("Segoe UI", 24, "bold"), fill="#ffd36c"))
        self.overlay_items.append(self.canvas.create_text(self.cw // 2, 390, text="Sharper human and animal visuals.\nBoat direction fixed.\nPress START GAME to begin.", font=("Segoe UI", 20, "bold"), fill="#dceeff", justify="center"))
        self.update_controls()

    def show_game_over(self, reason):
        self.clear_overlay()
        self.overlay_items.append(self.canvas.create_rectangle(150, 180, 950, 610, fill="#180d12", stipple="gray50", outline="#ff6d6d", width=4))
        self.overlay_items.append(self.canvas.create_text(550, 275, text="GAME OVER", font=("Segoe UI", 38, "bold"), fill="#ff7e7e"))
        self.overlay_items.append(self.canvas.create_text(550, 385, text=reason, font=("Segoe UI", 21, "bold"), fill="#ffe2e2", width=650, justify="center"))
        self.overlay_items.append(self.canvas.create_text(550, 520, text="Press RESTART to try again", font=("Segoe UI", 18, "bold"), fill="#ffd36c"))
        self.update_controls()

    def show_win_screen(self):
        self.clear_overlay()
        elapsed = max(0, self.root.tk.call("clock", "milliseconds") - self.start_ms) / 1000
        self.overlay_items.append(self.canvas.create_rectangle(130, 165, 970, 620, fill="#071725", stipple="gray50", outline="#ffd36c", width=4))
        self.overlay_items.append(self.canvas.create_text(550, 255, text="PUZZLE SOLVED", font=("Segoe UI", 40, "bold"), fill="#8dff9a"))
        self.overlay_items.append(self.canvas.create_text(550, 325, text="ULTRA PROMAX SUCCESS", font=("Segoe UI", 24, "bold"), fill="#ffd36c"))
        self.overlay_items.append(self.canvas.create_text(550, 410, text=f"Moves Used: {self.game.moves}", font=("Segoe UI", 20, "bold"), fill="#e7f4ff"))
        self.overlay_items.append(self.canvas.create_text(550, 455, text=f"Time: {elapsed:.1f} seconds", font=("Segoe UI", 20, "bold"), fill="#e7f4ff"))
        self.overlay_items.append(self.canvas.create_text(550, 540, text="Press RESTART to play again", font=("Segoe UI", 18, "bold"), fill="#ffcf74"))
        self.update_controls()

    def animation_loop(self):
        self.phase += 0.08
        self.wave += 0.12
        self.bob += 0.08
        self.spark += 0.15

        if not self.animating:
            old_overlay = list(self.overlay_items)
            self.draw_scene()
            if self.started:
                self.refresh_positions()
            for i in range(13):
                x = 240 + i * 48
                y = 240 + i * 37 % 450 + math.sin(self.wave + i * 0.8) * 8
                self.canvas.create_arc(x, y, x + 32, y + 12, start=0, extent=180, style="arc", outline="#eafcff", width=2)
            for idx, s in enumerate(self.stars):
                self.canvas.itemconfig(s, fill="#ffffff" if math.sin(self.spark + idx) > 0 else "#b8c8ff")
            if old_overlay:
                self.overlay_items = []
                for item in old_overlay:
                    pass
                if not self.started:
                    self.show_start_screen()
                elif self.game.won():
                    self.show_win_screen()
        self.root.after(70, self.animation_loop)


if __name__ == "__main__":
    root = tk.Tk()
    app = RiverCrossingUltraPromax(root)
    root.mainloop()
