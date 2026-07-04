# completely normal maze game
this is a completely normal maze game. we have a completely normal voxel-based maze, which has normal things like a player and walls and multiple rooms and definitely not things like invisible portals or impossible geometry in a world that has no permanence. definitely not.

---

But for real, now.
This is a game where you navigate slightly eerie mazes that just don't make sense. The world silently warps around you as you explore through it, never _quite_ letting you understand whats going on.

## Features

- GPU voxel raymarching (3D DDA)
- Face-based voxel data
- Procedural room builder
- ~~Portals with arbitrary transforms~~ (WIP)

---

## Next steps

[ ] Portal traversal
[ ] Collision Detection
[ ] Level editor (long term)

---

## Installation

To run the code, use the following bash. Make sure your python version is compliant with the requirements outlined in `pyproject.toml`

```bash
git clone https://github.com/ThatShushi17/normal-maze
cd ./normal-maze
python -m venv .venv
pip install -r requirements.txt

python main.py
```