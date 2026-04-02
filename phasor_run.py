#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║               NullPhasor's               ║
║            P H A S O R  R U N            ║
║   Run and jump.The sword doesn't work.   ║
╚══════════════════════════════════════════╝

A terminal-native endless runner.
Built for dark screens and fast fingers.

Controls : SPACE or ↑ to jump
           Q to quit

Tested on : Termux (Android), Linux, macOS
Requires  : Python 3.6+  (stdlib only, no pip needed)
"""

import curses
import time
import random

# ─── SETTINGS ───────────────────────────────────────────────────────────────

WIDTH           = 100
HEIGHT          = 20
GROUND_Y        = HEIGHT - 4
FPS             = 60
GRAVITY         = 0.35
JUMP_FORCE      = -4.0
GAME_SPEED_INIT = 0.045
SPEED_INCREMENT = 0.0015
SCORE_MILESTONE = 100       # speed bumps every N points

# ─── SPRITES ─────────────────────────────────────────────────────────────────
#
#  PHASOR (player) — 3 rows tall
#
#    o        <- head
#   /|\/     <- torso + both arms out
#    /\       <- legs, alternating stride
#
#  ENEMIES — 3 variants, all 3 rows tall
#
#  E1 standard :   @       E2 wide :    @       E3 elite :  [@]
#                 /|\               \/|\                  \ /V\}
#                  /\                  /\                   _/\_

PHASOR_FRAMES = [
    # frame 0 — right stride
    [" o   ",
     "/|\\/",
     " /\\  "],
    # frame 1 — left stride
    [" o   ",
     "/|\\/",
     "/  \\ "],
]

PHASOR_AIR = [
    "  o   ",
    " /|\\/",
    "  /\\  ",
]

PHASOR_DEAD = [
    "  x   ",
    " \\|/ ",
    " / \\ ",
]



ENEMY_SPRITES = [
    # variant 1 — standard
    [" @ ",
     "/|\\",
     " /\\ "],
    # variant 2 — arms wide
    ["  @  ",
     "\\/|\\",
     "  /\\ "],
    # variant 3 — elite (helmet + cape)
    ["[@] ",
     "\\ /V\\}",
     " _/\\_ "],
]

GROUND_CHAR = "─"
SCANLINE    = "·"

# ─── COLOR PAIRS ─────────────────────────────────────────────────────────────
# 1 = phasor / player     (bright green)
# 2 = ground + dim UI     (green, dim)
# 3 = enemy               (red)
# 4 = headers + borders   (cyan)
# 5 = death state         (red, bold)

# ─── PLAYER ──────────────────────────────────────────────────────────────────

class Phasor:
    def __init__(self):
        self.x          = 8
        self.y          = float(GROUND_Y - 3)   # 3 rows tall
        self.vy         = 0.0
        self.on_ground  = True
        self.frame      = 0
        self.frame_tick = 0
        self.dead       = False

    def jump(self):
        if self.on_ground:
            self.vy        = JUMP_FORCE
            self.on_ground = False

    def update(self):
        if not self.on_ground:
            self.vy += GRAVITY
            self.y  += self.vy
            if self.y >= GROUND_Y - 3:
                self.y         = float(GROUND_Y - 3)
                self.vy        = 0.0
                self.on_ground = True

        # walk animation only on ground
        if self.on_ground:
            self.frame_tick += 1
            if self.frame_tick >= 8:
                self.frame      = 1 - self.frame
                self.frame_tick = 0

    def get_sprite(self):
        if self.dead:
            return PHASOR_DEAD
        if not self.on_ground:
            return PHASOR_AIR
        return PHASOR_FRAMES[self.frame]

    def hitbox(self):
        # tight inner box — 1-cell margin on all sides for fairness
        return (int(self.y) + 1, self.x + 1, int(self.y) + 2, self.x + 2)


# ─── ENEMY ───────────────────────────────────────────────────────────────────

class Enemy:
    def __init__(self, x, speed_level=1):
        self.x      = x
        self.sprite = random.choice(ENEMY_SPRITES)
        self.width  = len(self.sprite[0])
        self.height = len(self.sprite)
        # randomised gap — shrinks with speed, always jumpable
        min_gap = max(18, 38 - speed_level * 2)
        max_gap = max(35, 70 - speed_level * 2)
        self.gap = random.randint(min_gap, max_gap)

    def hitbox(self):
        top = GROUND_Y - self.height
        return (top, self.x + 1, GROUND_Y - 1, self.x + self.width - 1)


# ─── COLLISION ───────────────────────────────────────────────────────────────

def check_collision(phasor, enemy):
    pt, pl, pb, pr = phasor.hitbox()
    et, el, eb, er = enemy.hitbox()
    return not (pb < et or pt > eb or pr < el or pl > er)


# ─── SAFE DRAW ───────────────────────────────────────────────────────────────

def safe_addstr(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h:
        return
    if x < 0:
        text = text[-x:]
        x    = 0
    if x >= w:
        return
    max_len = w - x - 1
    if max_len <= 0:
        return
    try:
        win.addstr(y, x, text[:max_len], attr)
    except curses.error:
        pass


# ─── DRAW FUNCTIONS ──────────────────────────────────────────────────────────

def draw_header(win, score, hi_score, speed_level):
    h, w = win.getmaxyx()
    border = "╔" + "═" * (w - 2) + "╗"
    safe_addstr(win, 0, 0, border, curses.color_pair(4))
    title = " N U L L P H A S O R  //  P H A S O R  R U N "
    safe_addstr(win, 0, (w - len(title)) // 2, title,
                curses.color_pair(4) | curses.A_BOLD)
    score_str = f"SCORE: {score:06d}  HI: {hi_score:06d}  LVL: {speed_level}"
    safe_addstr(win, 1, w - len(score_str) - 2, score_str, curses.color_pair(4))


def draw_ground(win, offset):
    h, w = win.getmaxyx()
    line = (GROUND_CHAR * (WIDTH + 10))
    safe_addstr(win, GROUND_Y,     1, line[:w - 2], curses.color_pair(2))
    safe_addstr(win, GROUND_Y + 1, 1, (SCANLINE * (w - 2))[:w - 2],
                curses.color_pair(2) | curses.A_DIM)


def draw_phasor(win, phasor):
    sprite = phasor.get_sprite()
    pair   = curses.color_pair(5) if phasor.dead else curses.color_pair(1)
    attr   = pair | curses.A_BOLD
    for i, row in enumerate(sprite):
        safe_addstr(win, int(phasor.y) + i, phasor.x, row, attr)


def draw_enemy(win, enemy):
    top_y = GROUND_Y - enemy.height
    for i, row in enumerate(enemy.sprite):
        safe_addstr(win, top_y + i, enemy.x, row,
                    curses.color_pair(3) | curses.A_BOLD)


def draw_you_died(win, score, hi_score):
    h, w = win.getmaxyx()
    cx   = w // 2
    new_best = score == hi_score and score > 0
    lines = [
        ("┌───────────────────────────────┐",  4),
        ("│                               │",  4),
        ("│      Y O U   D I E D          │",  5),
        ("│                               │",  4),
        (f"│   SCORE   :  {score:06d}           │", 4),
        (f"│   BEST    :  {hi_score:06d}           │", 4),
        ("│  ── NEW BEST! ──              │" if new_best
         else "│                               │",
         1 if new_best else 4),
        ("│                               │",  4),
        ("│   [SPACE]  to run again       │",  2),
        ("│   [Q]      to quit            │",  2),
        ("│                               │",  4),
        ("└───────────────────────────────┘",  4),
    ]
    start_y = h // 2 - len(lines) // 2
    for i, (line, pair) in enumerate(lines):
        safe_addstr(win, start_y + i, cx - len(line) // 2, line,
                    curses.color_pair(pair) | curses.A_BOLD)


def draw_start_screen(win):
    h, w = win.getmaxyx()
    cx   = w // 2
    lines = [
        ("╔═══════════════════════════════════════╗", 4),
        ("║                                       ║", 4),
        ("║             NullPhasor's              ║", 4),
        ("║         P H A S O R  R U N            ║", 2),
        ("║                                       ║", 4),
        ("║  Run and jump.The sword doesn't work  ║", 1),
        ("║                                       ║", 4),
        ("║      [SPACE]  to start running        ║", 2),
        ("║      [Q]      to exit                 ║", 2),
        ("║                                       ║", 4),
        ("╚═══════════════════════════════════════╝", 4),
    ]
    start_y = h // 2 - len(lines) // 2
    for i, (line, pair) in enumerate(lines):
        safe_addstr(win, start_y + i, cx - len(line) // 2, line,
                    curses.color_pair(pair) | curses.A_BOLD)


# ─── MAIN LOOP ───────────────────────────────────────────────────────────────

def game_loop(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_GREEN, -1)   # phasor
    curses.init_pair(2, curses.COLOR_GREEN, -1)   # ground
    curses.init_pair(3, curses.COLOR_RED,   -1)   # enemy
    curses.init_pair(4, curses.COLOR_CYAN,  -1)   # UI
    curses.init_pair(5, curses.COLOR_RED,   -1)   # death

    hi_score = 0

    # ── boot screen ──────────────────────────────────────────────────────────
    while True:
        stdscr.erase()
        draw_start_screen(stdscr)
        stdscr.refresh()
        k = stdscr.getch()
        if k in (ord('q'), ord('Q')):
            return
        if k == ord(' '):
            break
        time.sleep(0.05)

    # ── game loop ─────────────────────────────────────────────────────────────
    while True:                         # outer  — restart
        phasor        = Phasor()
        enemies       = []
        score         = 0
        ground_offset = 0.0
        game_speed    = GAME_SPEED_INIT
        speed_level   = 1
        dead          = False
        dead_timer    = 0

        while True:                     # inner  — one run
            frame_start = time.time()
            stdscr.erase()
            h, w = stdscr.getmaxyx()

            # input
            k = stdscr.getch()
            if k in (ord('q'), ord('Q')):
                return
            if not dead and k in (ord(' '), curses.KEY_UP):
                phasor.jump()
            if dead and k == ord(' '):
                break

            if not dead:
                # update physics
                phasor.update()
                ground_offset += game_speed * 30
                score         += 1

                # level up
                new_level = 1 + score // SCORE_MILESTONE
                if new_level > speed_level:
                    speed_level  = new_level
                    game_speed  += SPEED_INCREMENT

                # move enemies
                step = int(game_speed * 30) or 1
                for e in enemies:
                    e.x -= step

                # cull off-screen enemies
                enemies = [e for e in enemies if e.x + e.width > 0]

                # spawn next enemy with its own randomised gap
                spawn = not enemies or enemies[-1].x <= WIDTH - enemies[-1].gap
                if spawn:
                    enemies.append(Enemy(WIDTH + 2, speed_level))

                # collision check
                for e in enemies:
                    if check_collision(phasor, e):
                        phasor.dead = True
                        dead        = True
                        if score > hi_score:
                            hi_score = score
                        break

            else:
                dead_timer += 1

            # draw everything
            draw_header(stdscr, score, hi_score, speed_level)
            draw_ground(stdscr, ground_offset)
            for e in enemies:
                draw_enemy(stdscr, e)
            draw_phasor(stdscr, phasor)

            if dead:
                draw_you_died(stdscr, score, hi_score)

            safe_addstr(stdscr, h - 1, 1,
                        "SPACE / ↑  jump   │   Q  quit   │   nullphasor",
                        curses.color_pair(2) | curses.A_DIM)

            stdscr.refresh()

            # frame cap
            elapsed = time.time() - frame_start
            wait    = (1.0 / FPS) - elapsed
            if wait > 0:
                time.sleep(wait)

        # back to outer loop = new run


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

def main():
    try:
        curses.wrapper(game_loop)
    except KeyboardInterrupt:
        pass
    print("\n\033[32m[ nullphasor ]  phasor.run terminated.\033[0m\n")


if __name__ == "__main__":
    main()
