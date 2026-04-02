# PHASOR RUN
### by [NullPhasor](https://github.com/nullphasor)

```
╔══════════════════════════════════════════╗
║                NullPhasor's                     ║
║              P H A S O R   RUN                  ║
║     Run and jump.The sword doesn't work         ║
╚══════════════════════════════════════════╝
```

> A terminal-native endless runner. No browser. No install. Just Python and a dark screen.

---

## What is this

An endless runner that lives entirely in your terminal.  
You are **Phasor** — a lone figure running through an infinite corridor of sword-wielding enemies.  
Jump over them or die trying.

Built with Python's `curses` — zero dependencies, zero pip installs.  
Designed to look good on **Termux**, Linux, and macOS terminals.

---

## Run it

```bash
# clone
git clone https://github.com/nullphasor/phasor-run.git
cd phasor-run

# run
python phasor_run.py
```

> **Requirements:** Python 3.6+ only. That's it.

---

## Controls

| Key | Action |
|-----|--------|
| `SPACE` or `↑` | Jump |
| `Q` | Quit |

---

## Terminal setup (for best look)

- Font: **JetBrains Mono**, **Fira Code**, or any monospace with Unicode support
- Background: pure `#000000` black
- On Termux: increase font size so the game fills your screen, use **landscape mode**

---

## Features

- Human-shaped player sprite with walk animation and air pose
- Sword-wielding enemy variants — 3 different designs
- Randomised enemy spacing — no two runs feel the same
- Speed increases every 100 points — it gets harder
- **YOU DIED** screen with score, best score, and new-best detection
- Runs on Termux with zero setup

---

## File structure

```
phasor-run/
├── phasor_run.py   # entire game — single file
└── README.md
```

---

## License

MIT — use it, fork it, mod it.  
Credit appreciated but not required.

---

*nullphasor — terminal first. always.*


