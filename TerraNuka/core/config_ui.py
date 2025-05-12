# core/ui.py


if __name__ == "__main__":
    raise RuntimeError("This module is not meant to be run directly.")

import tkinter as tk
from tkinter import colorchooser
import random

from .config import WIDTH, bounds
from .terrain import Terrain
from .entities import Tank
from .enums import GameState

adjectives = [
    "Wiggly", "Brave", "Soggy", "Tiny", "Curious", "Nervous",
    "Fluffy", "Grumpy", "Sneaky", "Bouncy", "Moist", "Silly",
    "Sleepy", "Spicy", "Dry", "Bold", "Crazy", "Chubby", "Loud",
    "~Sgt.", "~Cpt.", "~Gen.", "~Maj.", "~Pvt.", "~Cpl.", "~Lt.", "~Col.",
    "~Shifu", "~Master", "~Sensei", "~Guru"
]
animals = [
    "Monkey", "Rock", "Bear", "Lizard", "Turtle", "Fish",
    "Penguin", "Tiger", "Duck", "Sloth", "Panther", "Elephant",
    "Giraffe", "Fox", "Moose", "Meerkat", "Panda", "Llama",
    "Koala", "Turtle", "Otter", "Hedgehog", "Raccoon",
    "Napkin", "Sponge", "Cactus", "Onion", "Beet"
]

current_state = GameState.MENU
menuconfig = None

class GameConfigUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Setup")

        self.players_frame = tk.LabelFrame(root, text="Players", padx=10, pady=10)
        self.players_frame.grid(row=0, column=0, padx=10, pady=10)

        self.num_players_var = tk.IntVar(value=2)
        tk.Label(self.players_frame, text="Number of Players:").grid(row=0, column=0)
        self.num_players_menu = tk.OptionMenu(self.players_frame, self.num_players_var, 2, 3, 4, 5, command=self.update_players)
        self.num_players_menu.grid(row=0, column=1)

        self.player_names = []
        self.player_widgets = []
        self.colors = []

        self.update_players(2)

        self.terrain_frame = tk.LabelFrame(root, text="Terrain", padx=10, pady=10)
        self.terrain_frame.grid(row=1, column=0, padx=10, pady=10)

        tk.Label(self.terrain_frame, text="Terrain Seed:").grid(row=0, column=0)
        vcmd = (self.root.register(self.is_digit_input), '%P')
        self.terrain_seed = tk.Entry(self.terrain_frame, validate="key", validatecommand=vcmd)
        self.terrain_seed.insert(0, str(random.randint(0, 100000)))
        self.terrain_seed.grid(row=0, column=1)
        self.terrain_seed.bind("<FocusOut>", self.clamp_seed)

        self.min_height_var = tk.IntVar(value=10)
        self.max_height_var = tk.IntVar(value=540)

        tk.Label(self.terrain_frame, text="Min Height:").grid(row=1, column=0)
        tk.Scale(self.terrain_frame, from_=0, to=200, orient='horizontal', variable=self.min_height_var).grid(row=1, column=1)

        tk.Label(self.terrain_frame, text="Max Height:").grid(row=2, column=0)
        tk.Scale(self.terrain_frame, from_=300, to=700, orient='horizontal', variable=self.max_height_var).grid(row=2, column=1)

        self.settings_frame = tk.LabelFrame(root, text="Gameplay Settings", padx=10, pady=10)
        self.settings_frame.grid(row=2, column=0, padx=10, pady=10)

        self.fuel_var = tk.DoubleVar(value=0.5)
        self.health_var = tk.IntVar(value=100)

        tk.Label(self.settings_frame, text="Fuel Amount:").grid(row=0, column=0)
        tk.Scale(self.settings_frame, from_=0.1, to=1.0, resolution=0.1, orient='horizontal', variable=self.fuel_var).grid(row=0, column=1)

        tk.Label(self.settings_frame, text="Tank Health:").grid(row=1, column=0)
        tk.Scale(self.settings_frame, from_=10, to=200, orient='horizontal', variable=self.health_var).grid(row=1, column=1)

        self.start_button = tk.Button(root, text="Start Game", command=self.collect_config)
        self.start_button.grid(row=3, column=0, pady=20)

    def is_digit_input(self, value):
        return value.isdigit() or value == ""

    def clamp_seed(self, *_):
        try:
            val_str = self.terrain_seed.get().strip()
            val = int(val_str) if val_str else random.randint(0, 100000)
            clamped = max(0, min(100000, val))
            self.terrain_seed.delete(0, tk.END)
            self.terrain_seed.insert(0, str(clamped))
        except ValueError:
            self.terrain_seed.delete(0, tk.END)
            self.terrain_seed.insert(0, str(random.randint(0, 100000)))

    def generate_random_name(self, index=None):
        adj = random.choice(adjectives)
        animal = random.choice(animals)
        name = f"The {adj} {animal}" if adj[0] != "~" else f"{adj[1:]} {animal}"
        if index is not None:
            self.player_names[index].delete(0, tk.END)
            self.player_names[index].insert(0, name)
        else:
            return name

    def update_players(self, count):
        for widgets in self.player_widgets:
            for widget in widgets:
                widget.destroy()
        self.player_widgets.clear()
        self.player_names.clear()
        self.colors.clear()

        color_options = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF",
            "#00FFFF", "#88FF00", "#FF8800", "#0088FF", "#8888FF"
        ]

        for i in range(self.num_players_var.get()):
            name_entry = tk.Entry(self.players_frame)
            name_entry.insert(0, self.generate_random_name())
            name_entry.grid(row=i + 1, column=0)

            random_btn = tk.Button(self.players_frame, text="🎲", command=lambda i=i: self.generate_random_name(i))
            random_btn.grid(row=i + 1, column=1)

            color = random.choice(color_options)
            self.colors.append(color)
            color_preview = tk.Label(self.players_frame, text="    ", bg=color)
            color_preview.grid(row=i + 1, column=2)

            color_button = tk.Button(self.players_frame, text="Choose Color", command=lambda i=i: self.choose_color(i))
            color_button.grid(row=i + 1, column=3)

            self.player_names.append(name_entry)
            self.player_widgets.append((name_entry, random_btn, color_preview, color_button))

    def choose_color(self, index):
        color = colorchooser.askcolor()[1]
        if color:
            self.colors[index] = color
            self.player_widgets[index][2].config(bg=color)

    def collect_config(self):
        global current_state, menuconfig
        player_data = []
        for idx, name_entry in enumerate(self.player_names):
            name = name_entry.get()
            hex_color = self.colors[idx]
            color = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
            player_data.append({"name": name, "color": color})

        menuconfig = {
            "players": player_data,
            "terrain_seed": self.terrain_seed.get(),
            "terrain_min_height": self.min_height_var.get(),
            "terrain_max_height": self.max_height_var.get(),
            "fuel": self.fuel_var.get(),
            "health": self.health_var.get()
        }

        current_state = GameState.PLAYING
        self.root.destroy()

def load_game_config():
    from .globals import terrain, tanks, config_loaded
    global menuconfig

    if menuconfig:
        tanks.clear()
        player_data = menuconfig["players"]
        terrain.seed = int(menuconfig["terrain_seed"])
        terrain.min_height = int(menuconfig["terrain_min_height"])
        terrain.max_height = int(menuconfig["terrain_max_height"])
        terrain.heightMap = terrain.generate_terrain()

        for i, player in enumerate(player_data):
            tank = Tank(
                height=12,
                width=24,
                name=player["name"],
                color=player["color"],
                fuel=float(menuconfig["fuel"]),
                health=float(menuconfig["health"]),
                max_health=float(menuconfig["health"]),
                x=(WIDTH // (len(player_data) + 1)) * (i + 1),
            )
            tank.cannonColor = tuple(255 - c for c in tank.color)
            tank.y = bounds.y2 - tank.height - tank.bottomCollide()
            tanks.append(tank)

        config_loaded[0] = True
