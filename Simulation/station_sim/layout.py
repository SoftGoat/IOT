from .config import LENGTH_M, PLAT_Y1

BENCHES = [
    dict(x=20, y=3.5, w=3.0, h=0.8),
    dict(x=50, y=3.5, w=3.0, h=0.8),
    dict(x=80, y=3.5, w=3.0, h=0.8),
]
KIOSK = dict(x=35, y=4.2, w=2.2, h=1.2)
STAIRS = [
    dict(x=5,  y=PLAT_Y1 - 1.2, w=2.5, h=1.2),
    dict(x=92, y=PLAT_Y1 - 1.2, w=2.5, h=1.2),
]
OBSTACLES = BENCHES + [KIOSK] + STAIRS

def make_doors(n: int):
    if n <= 0:
        return []
    spacing = LENGTH_M / (n + 1)
    return [(i + 1) * spacing for i in range(n)]
