"""Petite bibliothèque de dessin au style PowerAMC (symboles jaune pâle avec ombre, traits sombres)."""
import math

from PIL import Image, ImageDraw, ImageFont

S = 3          # sur-échantillonnage pour lisser les traits
OUT = 2        # taille finale = taille logique x 2 (image nette dans Word)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

YELLOW = (255, 255, 204)   # fond des symboles PowerAMC
LINE = (30, 30, 100)       # trait bleu nuit
SHADOW = (150, 150, 150)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGB", (w * S, h * S), WHITE)
        self.d = ImageDraw.Draw(self.im)
        self._fonts = {}

    # ---------- outils de base ----------
    def font(self, size=12, bold=False):
        key = (size, bold)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(BOLD if bold else FONT, int(size * S))
        return self._fonts[key]

    def tw(self, text, size=12, bold=False):
        return max(self.font(size, bold).getlength(line) for line in text.split("\n")) / S

    def p(self, v):
        return int(round(v * S))

    def text(self, x, y, s, size=12, bold=False, anchor="la", fill=BLACK, spacing=3):
        self.d.multiline_text((self.p(x), self.p(y)), s, font=self.font(size, bold), fill=fill,
                              anchor=anchor, align={"l": "left", "m": "center", "r": "right"}[anchor[0]],
                              spacing=self.p(spacing))

    def rect(self, x, y, w, h, fill=None, shadow=True, width=1):
        fill = YELLOW if fill is None else fill
        if shadow:
            self.d.rectangle([self.p(x + 4), self.p(y + 4), self.p(x + w + 4), self.p(y + h + 4)], fill=SHADOW)
        self.d.rectangle([self.p(x), self.p(y), self.p(x + w), self.p(y + h)], fill=fill, outline=LINE, width=self.p(width))

    def ellipse(self, cx, cy, w, h, fill=None, shadow=True):
        fill = YELLOW if fill is None else fill
        if shadow:
            self.d.ellipse([self.p(cx - w / 2 + 4), self.p(cy - h / 2 + 4), self.p(cx + w / 2 + 4), self.p(cy + h / 2 + 4)], fill=SHADOW)
        self.d.ellipse([self.p(cx - w / 2), self.p(cy - h / 2), self.p(cx + w / 2), self.p(cy + h / 2)],
                       fill=fill, outline=LINE, width=self.p(1))

    def line(self, pts, dash=False, width=1, fill=None):
        fill = LINE if fill is None else fill
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if not dash:
                self.d.line([self.p(x1), self.p(y1), self.p(x2), self.p(y2)], fill=fill, width=self.p(width))
                continue
            length = math.hypot(x2 - x1, y2 - y1)
            if length == 0:
                continue
            ux, uy = (x2 - x1) / length, (y2 - y1) / length
            pos = 0.0
            while pos < length:
                end = min(pos + 6, length)
                self.d.line([self.p(x1 + ux * pos), self.p(y1 + uy * pos), self.p(x1 + ux * end), self.p(y1 + uy * end)],
                            fill=fill, width=self.p(width))
                pos += 10

    def head(self, tip, frm, kind="filled", size=11):
        """Pointe de flèche en `tip`, la ligne venant de `frm`."""
        ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
        a1, a2 = ang + math.radians(155), ang - math.radians(155)
        left = (tip[0] + size * math.cos(a1), tip[1] + size * math.sin(a1))
        right = (tip[0] + size * math.cos(a2), tip[1] + size * math.sin(a2))
        poly = [(self.p(tip[0]), self.p(tip[1])), (self.p(left[0]), self.p(left[1])), (self.p(right[0]), self.p(right[1]))]
        if kind == "filled":
            self.d.polygon(poly, fill=LINE, outline=LINE)
        elif kind == "hollow":
            self.d.polygon(poly, fill=WHITE, outline=LINE)
        elif kind == "open":
            self.d.line([poly[1], poly[0], poly[2]], fill=LINE, width=self.p(1))
        elif kind in ("diamond", "diamond_hollow"):
            back = (tip[0] + 2 * size * 0.8 * math.cos(ang + math.pi), tip[1] + 2 * size * 0.8 * math.sin(ang + math.pi))
            quad = [poly[0], poly[1], (self.p(back[0]), self.p(back[1])), poly[2]]
            self.d.polygon(quad, fill=LINE if kind == "diamond" else WHITE, outline=LINE)

    def actor(self, x, y, label, size=12):
        """Bonhomme UML : (x, y) = centre de la tête ; renvoie le point central du corps."""
        r = 9
        self.d.ellipse([self.p(x - r), self.p(y - r), self.p(x + r), self.p(y + r)], fill=YELLOW, outline=LINE, width=self.p(1))
        self.line([(x, y + r), (x, y + r + 26)])
        self.line([(x - 18, y + r + 10), (x + 18, y + r + 10)])
        self.line([(x, y + r + 26), (x - 15, y + r + 48)])
        self.line([(x, y + r + 26), (x + 15, y + r + 48)])
        self.text(x, y + r + 56, label, size=size, bold=True, anchor="ma")
        return (x, y + r + 20)

    def label_over(self, x, y, label, size=12):
        """Réécrit le nom d'un acteur par-dessus les traits, sur fond blanc (lisible)."""
        w = self.tw(label, size, True)
        h = 16 * (label.count("\n") + 1)
        self.d.rectangle([self.p(x - w / 2 - 3), self.p(y - 1), self.p(x + w / 2 + 3), self.p(y + h + 1)], fill=WHITE)
        self.text(x, y, label, size=size, bold=True, anchor="ma")

    def save(self, path):
        self.im.resize((self.w * OUT, self.h * OUT), Image.LANCZOS).save(path, optimize=True)


# ---------- cas d'utilisation ----------
def usecase(cv, cx, cy, label, minw=0):
    w = max(cv.tw(label) + 56, minw)
    h = 22 * (label.count("\n") + 1) + 30
    cv.ellipse(cx, cy, w, h)
    cv.text(cx, cy, label, anchor="mm")
    return {"cx": cx, "cy": cy, "w": w, "h": h}


def edge_point(uc, tx, ty):
    """Point du bord de l'ellipse `uc` dans la direction (tx, ty)."""
    dx, dy = tx - uc["cx"], ty - uc["cy"]
    a, b = uc["w"] / 2, uc["h"] / 2
    t = 1 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2) if (dx or dy) else 0
    return (uc["cx"] + dx * t, uc["cy"] + dy * t)


def associate(cv, pt, uc):
    cv.line([pt, edge_point(uc, *pt)])


def associate_side(cv, pt, uc, side="left"):
    """Trait horizontal-ish vers le bord gauche (ou droit) de l'ellipse : évite de traverser les voisines."""
    x = uc["cx"] - uc["w"] / 2 if side == "left" else uc["cx"] + uc["w"] / 2
    cv.line([pt, (x, uc["cy"])])


def link_uc(cv, a, b, label):
    """Flèche pointillée a -> b avec stéréotype («include» / «extend»)."""
    p1, p2 = edge_point(a, b["cx"], b["cy"]), edge_point(b, a["cx"], a["cy"])
    cv.line([p1, p2], dash=True)
    cv.head(p2, p1, "open")
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    cv.d.rectangle([cv.p(mx - cv.tw(label, 11) / 2 - 3), cv.p(my - 9), cv.p(mx + cv.tw(label, 11) / 2 + 3), cv.p(my + 9)], fill=WHITE)
    cv.text(mx, my, label, size=11, anchor="mm")


# ---------- classes ----------
def class_box(cv, x, y, w, name, attrs, ops=(), stereotype=None):
    lh = 17
    head_h = 34 + (16 if stereotype else 0)
    a_h = lh * len(attrs) + 12
    o_h = (lh * len(ops) + 12) if ops else 0
    h = head_h + a_h + o_h
    cv.rect(x, y, w, h)
    cy = y + 10
    if stereotype:
        cv.text(x + w / 2, cy, f"«{stereotype}»", size=11, anchor="ma")
        cy += 16
    cv.text(x + w / 2, cy, name, size=13, bold=True, anchor="ma")
    cv.line([(x, y + head_h), (x + w, y + head_h)])
    for i, a in enumerate(attrs):
        cv.text(x + 10, y + head_h + 7 + i * lh, a, size=11)
    if ops:
        cv.line([(x, y + head_h + a_h), (x + w, y + head_h + a_h)])
        for i, o in enumerate(ops):
            cv.text(x + 10, y + head_h + a_h + 7 + i * lh, o, size=11)
    return {"x": x, "y": y, "w": w, "h": h}


# ---------- séquence ----------
def sequence(path, lifelines, steps, gap=300, left=110, header=64, step_h=48, extra_w=130, numbered=False):
    n = len(lifelines)
    xs = [left + i * gap for i in range(n)]
    idx = {name: i for i, (name, _) in enumerate(lifelines)}
    y = header + 70
    placed, frames, open_frames, acts, stack = [], [], [], [], {}
    num = 0
    for st in steps:
        kind = st[0]
        if kind == "msg":
            _, a, b, label, style, act = (st + (False,))[:6] if len(st) == 5 else st
            num += 1
            placed.append(("msg", y, idx[a], idx[b], f"{num} : {label}" if numbered else label, style))
            if style == "call" and act:
                stack.setdefault(b, []).append(y)
            if style == "return" and stack.get(a):
                acts.append((idx[a], stack[a].pop() - 8, y + 6))
            y += step_h + 12 * label.count("\n")
        elif kind == "self":
            _, a, label, act = st
            num += 1
            placed.append(("self", y, idx[a], f"{num} : {label}" if numbered else label))
            acts.append((idx[a], y - 8, y + 34))
            y += 62 + 12 * label.count("\n")
        elif kind in ("alt", "opt", "loop"):
            open_frames.append({"type": kind, "guard": st[1], "y1": y - 6, "elses": []})
            y += 30
        elif kind == "else":
            open_frames[-1]["elses"].append((y - 4, st[1]))
            y += 28
        elif kind == "end":
            f = open_frames.pop()
            f["y2"] = y - 8
            frames.append(f)
            y += 14
    total_h = y + 40
    cv = Canvas(xs[-1] + extra_w + 40, total_h)
    # en-têtes + lignes de vie
    for (name, kind), x in zip(lifelines, xs):
        if kind == "actor":
            cv.actor(x, 24, name)
        else:
            w = max(150, cv.tw(name) + 30)
            cv.rect(x - w / 2, 14, w, 40)
            cv.text(x, 34, name, anchor="mm", bold=True)
        cv.line([(x, header + (38 if kind == "actor" else 14)), (x, total_h - 20)], dash=True)
    # fragments combinés
    for f in frames:
        x1, x2 = xs[0] - 55, xs[-1] + 55
        cv.d.rectangle([cv.p(x1), cv.p(f["y1"]), cv.p(x2), cv.p(f["y2"])], outline=LINE, width=cv.p(1))
        tab_w = cv.tw(f["type"], 11, True) + 18
        cv.d.polygon([(cv.p(x1), cv.p(f["y1"])), (cv.p(x1 + tab_w), cv.p(f["y1"])), (cv.p(x1 + tab_w), cv.p(f["y1"] + 12)),
                      (cv.p(x1 + tab_w - 8), cv.p(f["y1"] + 20)), (cv.p(x1), cv.p(f["y1"] + 20))], fill=YELLOW, outline=LINE)
        cv.text(x1 + 8, f["y1"] + 3, f["type"], size=11, bold=True)
        g1 = f"[{f['guard']}]"
        cv.d.rectangle([cv.p(x1 + tab_w + 5), cv.p(f["y1"] + 2), cv.p(x1 + tab_w + 11 + cv.tw(g1, 11)), cv.p(f["y1"] + 19)], fill=WHITE)
        cv.text(x1 + tab_w + 8, f["y1"] + 4, g1, size=11)
        for ey, guard in f["elses"]:
            cv.line([(x1, ey), (x2, ey)], dash=True)
            g2 = f"[{guard}]"
            cv.d.rectangle([cv.p(x1 + 5), cv.p(ey + 2), cv.p(x1 + 11 + cv.tw(g2, 11)), cv.p(ey + 19)], fill=WHITE)
            cv.text(x1 + 8, ey + 4, g2, size=11)
    # barres d'activation
    for li, y1, y2 in acts:
        cv.rect(xs[li] - 6, y1, 12, y2 - y1, shadow=False)
    # messages
    for it in placed:
        if it[0] == "msg":
            _, my, ia, ib, label, style = it
            xa = xs[ia] + (6 if xs[ib] > xs[ia] else -6)
            xb = xs[ib] + (-6 if xs[ib] > xs[ia] else 6)
            cv.line([(xa, my), (xb, my)], dash=(style == "return"))
            cv.head((xb, my), (xa, my), "open" if style == "return" else "filled")
            lw = cv.tw(label, 11)
            lines = label.count("\n") + 1
            cv.d.rectangle([cv.p((xa + xb) / 2 - lw / 2 - 3), cv.p(my - 9 - 14 * lines), cv.p((xa + xb) / 2 + lw / 2 + 3), cv.p(my - 4)], fill=WHITE)
            cv.text((xa + xb) / 2, my - 7, label, size=11, anchor="md")
        else:
            _, my, ia, label = it
            x = xs[ia] + 6
            cv.line([(x, my), (x + 46, my), (x + 46, my + 26), (x, my + 26)])
            cv.head((x, my + 26), (x + 46, my + 26), "filled")
            cv.text(x + 54, my + 13, label, size=11, anchor="lm")
    cv.save(path)


# ---------- déploiement / états ----------
def node3d(cv, x, y, w, h, title, stereotype="device", dashed=False):
    """Nœud de déploiement en forme de cube, comme dans PowerAMC."""
    d = 14
    front = [cv.p(x), cv.p(y + d), cv.p(x + w), cv.p(y + h)]
    top = [(cv.p(x), cv.p(y + d)), (cv.p(x + d), cv.p(y)), (cv.p(x + w + d), cv.p(y)), (cv.p(x + w), cv.p(y + d))]
    right = [(cv.p(x + w), cv.p(y + d)), (cv.p(x + w + d), cv.p(y)), (cv.p(x + w + d), cv.p(y + h - d)), (cv.p(x + w), cv.p(y + h))]
    cv.d.polygon(top, fill=(235, 235, 170), outline=LINE)
    cv.d.polygon(right, fill=(215, 215, 150), outline=LINE)
    cv.d.rectangle(front, fill=YELLOW, outline=LINE, width=cv.p(1))
    cv.text(x + w / 2, y + d + 8, f"«{stereotype}»", size=10, anchor="ma")
    cv.text(x + w / 2, y + d + 22, title, size=12, bold=True, anchor="ma")
    return {"x": x, "y": y + d, "w": w, "h": h - d}


def component(cv, x, y, w, h, label):
    cv.rect(x, y, w, h, shadow=False)
    cv.rect(x - 9, y + h / 2 - 16, 18, 8, shadow=False)
    cv.rect(x - 9, y + h / 2 + 4, 18, 8, shadow=False)
    cv.text(x + w / 2 + 4, y + h / 2, label, size=11, anchor="mm")
    return {"x": x, "y": y, "w": w, "h": h}


def elbow(cv, pts, label=None, lx=None, ly=None, dash=False, head=True):
    cv.line(pts, dash=dash)
    if head:
        cv.head(pts[-1], pts[-2], "open")
    if label:
        w = cv.tw(label, 11)
        cv.d.rectangle([cv.p(lx - w / 2 - 3), cv.p(ly - 9), cv.p(lx + w / 2 + 3), cv.p(ly + 9 + 14 * label.count("\n"))], fill=WHITE)
        cv.text(lx, ly, label, size=11, anchor="ma")


def state(cv, cx, cy, w, h, label):
    cv.d.rounded_rectangle([cv.p(cx - w / 2 + 4), cv.p(cy - h / 2 + 4), cv.p(cx + w / 2 + 4), cv.p(cy + h / 2 + 4)], radius=cv.p(22), fill=SHADOW)
    cv.d.rounded_rectangle([cv.p(cx - w / 2), cv.p(cy - h / 2), cv.p(cx + w / 2), cv.p(cy + h / 2)], radius=cv.p(22), fill=YELLOW,
                           outline=LINE, width=cv.p(1))
    cv.text(cx, cy, label, size=13, bold=True, anchor="mm")
    return {"cx": cx, "cy": cy, "w": w, "h": h}


# ---------- activité ----------
def action(cv, cx, cy, label, w=220):
    h = 20 * (label.count("\n") + 1) + 22
    cv.d.rounded_rectangle([cv.p(cx - w / 2 + 4), cv.p(cy - h / 2 + 4), cv.p(cx + w / 2 + 4), cv.p(cy + h / 2 + 4)], radius=cv.p(16), fill=SHADOW)
    cv.d.rounded_rectangle([cv.p(cx - w / 2), cv.p(cy - h / 2), cv.p(cx + w / 2), cv.p(cy + h / 2)], radius=cv.p(16), fill=YELLOW,
                           outline=LINE, width=cv.p(1))
    cv.text(cx, cy, label, size=11, anchor="mm")
    return {"cx": cx, "cy": cy, "w": w, "h": h, "l": cx - w / 2, "r": cx + w / 2, "t": cy - h / 2, "b": cy + h / 2}


def decision(cv, cx, cy, label, w=210, h=96):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    cv.d.polygon([(cv.p(x + 4), cv.p(y + 4)) for x, y in pts], fill=SHADOW)
    cv.d.polygon([(cv.p(x), cv.p(y)) for x, y in pts], fill=YELLOW, outline=LINE)
    cv.text(cx, cy, label, size=11, anchor="mm")
    return {"cx": cx, "cy": cy, "t": cy - h / 2, "b": cy + h / 2, "l": cx - w / 2, "r": cx + w / 2}


def initial_node(cv, cx, cy):
    cv.d.ellipse([cv.p(cx - 10), cv.p(cy - 10), cv.p(cx + 10), cv.p(cy + 10)], fill=BLACK)
    return {"cx": cx, "cy": cy, "t": cy - 10, "b": cy + 10, "l": cx - 10, "r": cx + 10}


def final_node(cv, cx, cy):
    cv.d.ellipse([cv.p(cx - 15), cv.p(cy - 15), cv.p(cx + 15), cv.p(cy + 15)], fill=WHITE, outline=LINE, width=cv.p(2))
    cv.d.ellipse([cv.p(cx - 9), cv.p(cy - 9), cv.p(cx + 9), cv.p(cy + 9)], fill=BLACK)
    return {"cx": cx, "cy": cy, "t": cy - 15, "b": cy + 15, "l": cx - 15, "r": cx + 15}


# ---------- communication ----------
def comm_object(cv, cx, cy, label, w=170, h=44, actor=False, fs=12):
    if actor:
        cv.actor(cx, cy - 36, "")
        cv.text(cx, cy + 36, label, size=fs, bold=True, anchor="ma")
        return {"cx": cx, "cy": cy, "l": cx - 26, "r": cx + 26, "t": cy - 38, "b": cy + 34}
    cv.rect(cx - w / 2, cy - h / 2, w, h)
    tw = cv.tw(label, fs, True)
    cv.text(cx, cy, label, size=fs, bold=True, anchor="mm")
    cv.line([(cx - tw / 2, cy + 9), (cx + tw / 2, cy + 9)], width=1, fill=BLACK)
    return {"cx": cx, "cy": cy, "l": cx - w / 2, "r": cx + w / 2, "t": cy - h / 2, "b": cy + h / 2}


def comm_messages(cv, x1, x2, y_line, rows, above=True, fs=11):
    """Messages numérotés posés le long d'un lien horizontal ; chaque ligne = (texte, sens) avec sens '>' ou '<'."""
    n = len(rows)
    mid = (x1 + x2) / 2
    for i, (text, sens) in enumerate(rows):
        step = fs * 2 + 2
        y = y_line - 18 - (n - 1 - i) * step if above else y_line + 18 + i * step
        tw = cv.tw(text, fs)
        total = 34 + 8 + tw
        x0 = mid - total / 2
        cv.line([(x0, y), (x0 + 30, y)])
        if sens == ">":
            cv.head((x0 + 32, y), (x0, y), "filled", size=8)
        else:
            cv.head((x0, y), (x0 + 30, y), "filled", size=8)
        cv.text(x0 + 42, y, text, size=fs, anchor="lm")
