"""ASCII-Weihnachtsbaum: erst baut sich der Baum auf, dann kommt die
Deko, dazu funkeln im Hintergrund Sterne. Beenden mit Strg+C.

Braucht keine Zusatzpakete, nur ein Terminal mit Truecolor.
"""
import math
import random
import shutil
import sys
import time

FPS = 30
RESET = "\033[0m"
TEXT = "Frohe Weihnachten!"


def fg(r, g, b):
    return f"\033[38;2;{int(r)};{int(g)};{int(b)}m"


def scale(color, f):
    return tuple(min(255, c * f) for c in color)


class Scene:
    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        # Baumhoehe so waehlen, dass alles ins Fenster passt
        self.H = max(5, min(rows - 8, (cols - 5) // 2, 20))
        self.cx = cols // 2
        self.top = max(2, (rows - (self.H + 5)) // 2 + 1)

        # --- Baum: pro Zeile eine Liste von Zellen (x, y, Zeichen, Farbe)
        self.tree_rows = []
        for i in range(self.H):
            y = self.top + i
            row = []
            for x in range(self.cx - i, self.cx + i + 1):
                ch = random.choice("^^^*&")
                g = random.randint(110, 200)
                row.append((x, y, ch, (20, g, 40)))
            self.tree_rows.append(row)

        # --- Stamm
        self.trunk = [(x, self.top + self.H + k, "#", (120, 75, 30))
                      for k in range(2) for x in range(self.cx - 1, self.cx + 2)]

        # --- Deko: zufaellige Zellen im Inneren des Baums
        inner = [(x, y) for i, row in enumerate(self.tree_rows) if i >= 2
                 for (x, y, _, _) in row[1:-1]]
        random.shuffle(inner)
        palette = [(255, 60, 60), (255, 210, 60), (80, 140, 255),
                   (255, 100, 220), (240, 240, 240)]
        self.decos = [(x, y, random.choice(palette), random.uniform(0, 6.28))
                      for x, y in inner[: self.H * 2]]

        # --- Hintergrundsterne (nicht im Baum)
        self.stars = []
        for _ in range(cols * rows // 35):
            x, y = random.randrange(cols), random.randrange(rows - 1)
            if self.in_tree(x, y):
                continue
            self.stars.append((x, y, random.uniform(0, 6.28),
                               random.uniform(1.5, 4.0),
                               random.randint(0, 60)))

        # Zeitplan (in Frames)
        self.rows_every = 3
        self.deco_start = self.rows_every * self.H + 15
        self.deco_every = 3
        self.text_start = self.deco_start + self.deco_every * len(self.decos) + 20

    def in_tree(self, x, y):
        t = self.top
        if y == t + self.H + 3 and abs(x - self.cx) <= len(TEXT) // 2 + 2:
            return True  # Platz fuer den Text freihalten
        if y < t - 2 or y > t + self.H + 2:
            return False
        half = max(0, min(y - t, self.H - 1))
        return abs(x - self.cx) <= half + 2

    def frame(self, f):
        """Gibt den String fuer Frame f zurueck (nur Zellen mit Positionierung)."""
        t = f / FPS
        out = []

        def put(x, y, ch, color):
            if 0 <= x < self.cols and 0 <= y < self.rows - 1:
                out.append(f"\033[{y + 1};{x + 1}H{fg(*color)}{ch}")

        # Sterne
        for x, y, ph, sp, appear in self.stars:
            if f < appear:
                continue
            b = (math.sin(t * sp + ph) + 1) / 2
            ch = "." if b < 0.35 else "+" if b < 0.7 else "*"
            v = 70 + 185 * b
            put(x, y, ch, (v, v, min(255, v + 20)))

        # Baum Zeile fuer Zeile
        visible = min(self.H, f // self.rows_every)
        for row in self.tree_rows[:visible]:
            for x, y, ch, c in row:
                put(x, y, ch, c)
        if visible >= self.H:
            for x, y, ch, c in self.trunk:
                put(x, y, ch, c)

        # Stern auf der Spitze (erscheint mit der ersten Deko)
        if f >= self.deco_start:
            pulse = 0.75 + 0.25 * math.sin(t * 5)
            put(self.cx, self.top - 1, "*", scale((255, 220, 70), pulse))

        # Deko
        n = 0 if f < self.deco_start else (f - self.deco_start) // self.deco_every + 1
        for x, y, c, ph in self.decos[:n]:
            put(x, y, "o", scale(c, 0.7 + 0.3 * math.sin(t * 3 + ph)))

        # Text
        if f >= self.text_start:
            k = min(len(TEXT), (f - self.text_start) // 2 + 1)
            x0 = self.cx - len(TEXT) // 2
            y = self.top + self.H + 3
            for i, ch in enumerate(TEXT[:k]):
                put(x0 + i, y, ch, (255, 235, 235))

        out.append(RESET)
        return "".join(out)


def main():
    cols, rows = shutil.get_terminal_size()
    scene = Scene(cols, rows)
    w = sys.stdout.write
    w("\033[?1049h\033[?25l\033[2J")  # Alternativ-Bildschirm, Cursor aus, leeren
    try:
        f = 0
        while True:
            start = time.time()
            w(scene.frame(f))
            sys.stdout.flush()
            f += 1
            time.sleep(max(0, 1 / FPS - (time.time() - start)))
    except KeyboardInterrupt:
        pass
    finally:
        w(RESET + "\033[?25h\033[?1049l")  # Cursor an, normaler Bildschirm
        sys.stdout.flush()


if __name__ == "__main__":
    main()
