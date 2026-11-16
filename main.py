from PIL import Image

CHARS = "@%#*+=-:. "  # dunkel -> hell

def ascii_color(path, width=115):
    img = Image.open(path).convert("RGB")
    h = int(img.height / img.width * width * 0.5)
    img = img.resize((width, h))
    lines = []
    for y in range(h):
        row = ""
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            lum = 0.299*r + 0.587*g + 0.114*b
            ch = CHARS[int(lum / 256 * len(CHARS))]
            row += f"\033[38;2;{r};{g};{b}m{ch}"
        lines.append(row + "\033[0m")
    print("\n".join(lines))

ascii_color("roseV1.jpg")