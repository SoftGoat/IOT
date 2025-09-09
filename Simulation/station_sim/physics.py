import math, random
from .config import PLAT_Y0, PLAT_Y1, AGENT_RADIUS, CELL_SIZE
from .layout import OBSTACLES, STAIRS

def _aabb_contains(x, y, ob):
    return (ob["x"] <= x <= ob["x"] + ob["w"]) and (ob["y"] <= y <= ob["y"] + ob["h"])

def collides_any(x, y):
    if y < PLAT_Y0 or y > PLAT_Y1:
        return True
    # Treat agent as a disk; cheap test: center against obstacle AABBs with a margin
    for ob in OBSTACLES:
        if ob in STAIRS:
            continue
        # Inflate obstacle by radius
        if (ob["x"] - AGENT_RADIUS <= x <= ob["x"] + ob["w"] + AGENT_RADIUS and
            ob["y"] - AGENT_RADIUS <= y <= ob["y"] + ob["h"] + AGENT_RADIUS):
            return True
    return False

def next_pos_with_avoid(ax, ay, tx, ty, step):
    # This line was likely missing in your file, causing the error.
    dx, dy = tx - ax, ty - ay
    dist = math.hypot(dx, dy) or 1e-9
    nx, ny = dx / dist, dy / dist

    # 1. Arrival Behavior: Slow down when near the target
    slowing_dist = 3.0  # Slow down within 3 meters of target
    effective_step = step
    if dist < slowing_dist:
        effective_step = step * (dist / slowing_dist)

    # 2. Path Imperfection: Add a random "wobble"
    wobble = random.uniform(-0.4, 0.4)
    dir_x = nx - wobble * ny
    dir_y = ny + wobble * nx
    n_dist = math.hypot(dir_x, dir_y) or 1e-9
    dir_x /= n_dist
    dir_y /= n_dist

    cand = (ax + dir_x * effective_step, ay + dir_y * effective_step)
    if not collides_any(*cand):
        return cand

    # Obstacle avoidance (nudge sideways)
    side = 1 if ay < (PLAT_Y1 + PLAT_Y0) * 0.5 else -1
    for k in (0.3, 0.6):
        for s in (1, -1):
            ox = ax + dir_x * effective_step + s * side * 0.7 * k
            oy = ay + dir_y * effective_step + s * side * k
            if not collides_any(ox, oy):
                return ox, oy
    return ax, ay
 

def build_grid(agents, active_idx, grid_w, grid_h):
    buckets = [[] for _ in range(grid_w * grid_h)]
    for i in active_idx:
        a = agents[i]
        gx = int(a.x / CELL_SIZE)
        gy = int(a.y / CELL_SIZE)
        if 0 <= gx < grid_w and 0 <= gy < grid_h:
            buckets[gy * grid_w + gx].append(i)
    return buckets

def resolve_agent_collisions(agents, active_idx, grid_w, grid_h):
    for _ in range(3):  # simple relaxation
        buckets = build_grid(agents, active_idx, grid_w, grid_h)
        ax_adj = [(0.0, 0.0) for _ in agents]
        for gx in range(grid_w):
            for gy in range(grid_h):
                idxs = buckets[gy * grid_w + gx]
                # same-cell pairs
                for u in range(len(idxs)):
                    i = idxs[u]; a = agents[i]
                    for v in range(u + 1, len(idxs)):
                        j = idxs[v]; b = agents[j]
                        _resolve_pair(i, j, a, b, ax_adj)
                # neighbor cells (avoid double counting)
                for dx, dy in ((1,0),(1,1),(0,1),(-1,1)):
                    ngx, ngy = gx + dx, gy + dy
                    if 0 <= ngx < grid_w and 0 <= ngy < grid_h:
                        for i in idxs:
                            a = agents[i]
                            for j in buckets[ngy * grid_w + ngx]:
                                _resolve_pair(i, j, a, agents[j], ax_adj)
        for i in active_idx:
            dx, dy = ax_adj[i]
            nx, ny = agents[i].x + dx, agents[i].y + dy
            if not collides_any(nx, ny):
                agents[i].x, agents[i].y = nx, ny

def _resolve_pair(i, j, a, b, ax_adj):
    dx = a.x - b.x
    dy = a.y - b.y
    dist = math.hypot(dx, dy)
    # Agents can now get closer, allowing their visual circles to overlap.
    if dist < 1e-6 or dist >=  AGENT_RADIUS:
        return
    overlap = AGENT_RADIUS - dist
    nx = dx / dist if dist > 1e-6 else random.uniform(-1, 1)
    ny = dy / dist if dist > 1e-6 else random.uniform(-1, 1)
    push = overlap / 2
    ax_adj[i] = (ax_adj[i][0] + nx * push, ax_adj[i][1] + ny * push)
    ax_adj[j] = (ax_adj[j][0] - nx * push, ax_adj[j][1] - ny * push)
