# TerraNuka
A Scorched Earth-inspired 2D artillery game built in Python with Pygame and a Tkinter-based setup menu. Customize your players, terrain, and settings — then blast your friends into pixel dust.

## 🚀 Features
* Procedural terrain generation with Perlin noise

* Local multiplayer (2+ players)

* Angle + power control cannon system

* Explosions with terrain destruction and gravity-based collapse

* Firework show on game over 🎆

* Simple HUD with fuel, power, and health display

* Menu system to customize tanks, terrain, and game balance

## 📁 Project Structure
```
TerraNuka/
├── main.py                # Game entry point
├── assets/                # Sounds
├── core/                  # Game logic modules
│   ├── config.py          # Constants, bounds
│   ├── drawing.py         # HUD, explosion previews, health bars
│   ├── entities.py        # Tanks, Projectiles, Fireworks
│   ├── enums.py           # Game state enums
│   ├── globals.py         # Shared runtime state & sounds
│   ├── physics.py         # Collision, gravity, explosion logic
│   ├── terrain.py         # Terrain generation
│   └── ui.py              # Tkinter game setup menu
```
## 🛠️ Setup Instructions
1. Clone the repo
```
git clone https://github.com/yourusername/TerraNuka.git
cd TerraNuka
```
2. Create and activate a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
## ▶️ Running the Game
```
cd TerraNuka
python3 main.py
A Tkinter menu will open. After selecting your options, the game window will start.
```

## 🧱 Requirements
* Python 3.8+

* Pygame

* noise (Perlin terrain generation)

* Tkinter (usually comes with Python)

If tkinter is missing on Debian/Ubuntu:

```
sudo apt install python3-tk
```
## 🔊 Sound Credits
All sounds are already royalty free, but feel free to replace assets/sounds/ with your own effects or other royalty-free audio.

##  ✅ To Do (Pull Requests Welcome!)
* Add wind effects 🌬️

* Expand missile types

* Add AI bots

* Add high score tracking

* Polish game over screen