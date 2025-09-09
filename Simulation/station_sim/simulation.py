import sys, random, pygame
from collections import deque
from .config import (
    W, H, UI_W, SIM_W,
    INIT_PASS, INIT_DOORS, INIT_SPEED, INIT_BOARD,
    DT_CAP, AGENT_RADIUS, CELL_SIZE, LENGTH_M, PLAT_Y0, PLAT_Y1,
    QUEUE_JOIN_DISTANCE
)
from .coords import ScreenMapper
from .layout import make_doors
from .spawn import spawn_agents
from .physics import next_pos_with_avoid, resolve_agent_collisions
from .render import draw_layout, draw_agents, draw_heatmap, draw_stats, draw_title, Fonts
from .ui import build_ui
from .logging_utils import log_simulation_results

def run():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock  = pygame.time.Clock()
    pygame.display.set_caption("Train Station (Pygame) — with UI")

    fonts = Fonts()
    mapper = ScreenMapper()

    panel, sliders, btn_pause, btn_apply, btn_reset = build_ui(fonts.l, fonts.m, fonts.s, width=UI_W, height=H)
    paused = False

    n_pass  = int(sliders[0].value) if sliders else INIT_PASS
    n_doors = int(sliders[1].value) if sliders else INIT_DOORS
    mean_sp = float(sliders[2].value) if sliders else INIT_SPEED
    # The UI's "Board rate" slider now controls how often ranks of 3 can board.
    board_rate_setting = float(sliders[3].value) if sliders else INIT_BOARD
    BOARDING_INTERVAL = 3.0 / board_rate_setting # Time to board one rank of 3

    door_x = make_doors(n_doors)
    agents = spawn_agents(n_pass, door_x, mean_sp)

    # --- NEW QUEUEING SYSTEM SETUP ---
    queues = [deque() for _ in door_x]
    # Pre-calculate physical (x, y) positions for queue slots for each door
    slot_spacing = AGENT_RADIUS * 2.5
    queue_slots = [[(dx, PLAT_Y0 + 0.5 + i * slot_spacing) for i in range(n_pass)] for dx in door_x]
    # Assign agents to a queue and set their initial 'seeking' target
    if door_x:
        for agent in agents:
            # Note: spawn_agents still returns agents with a .target (float)
            d_idx = min(range(len(door_x)), key=lambda k: abs(agent.target - door_x[k]))
            agent.queue_idx = d_idx
            agent.state = 'seeking'
            # Initially, agents seek a general area near the back of the queue
            agent.target_pos = queue_slots[d_idx][10]

    boarding_timer = 0.0
    t = 0.0
    boarded_total = 0
    simulation_complete = False
    grid_w = int(LENGTH_M / CELL_SIZE) + 2
    grid_h = int(PLAT_Y1 / CELL_SIZE) + 2

    while True:
        dt_ms = clock.tick(60)
        dt = min(dt_ms / 1000.0, DT_CAP)

        # Reset button clicked state once per frame before handling events
        btn_pause.clicked = False
        btn_apply.clicked = False
        btn_reset.clicked = False

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit(); sys.exit(0)
                if ev.key == pygame.K_SPACE:
                    paused = not paused
                if ev.key == pygame.K_r:
                    btn_reset.clicked = True

            # panel-local mouse coords
            panel_local = None
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if SIM_W <= ev.pos[0] < SIM_W + UI_W:
                    panel_local = (ev.pos[0] - SIM_W, ev.pos[1])

            for s in sliders: s.handle(ev, panel_local)
            btn_pause.handle(ev, panel_local)
            btn_apply.handle(ev, panel_local)
            btn_reset.handle(ev, panel_local)

        if btn_pause.clicked:
            paused = not paused
        
        if btn_apply.clicked:
            n_pass  = int(sliders[0].value)
            n_doors = int(sliders[1].value)
            mean_sp = float(sliders[2].value)
            board_rate_setting = float(sliders[3].value)
            BOARDING_INTERVAL = 3.0 / board_rate_setting
            # Flag a reset to apply new settings
            btn_reset.clicked = True

        if btn_reset.clicked:
            door_x = make_doors(n_doors)
            agents = spawn_agents(n_pass, door_x, mean_sp)
            queues = [deque() for _ in door_x]
            queue_slots = [[(dx, PLAT_Y0 + 0.5 + i * slot_spacing) for i in range(n_pass)] for dx in door_x]
            if door_x:
                for agent in agents:
                    d_idx = min(range(len(door_x)), key=lambda k: abs(agent.target - door_x[k]))
                    agent.queue_idx = d_idx
                    agent.state = 'seeking'
                    agent.target_pos = queue_slots[d_idx][10]

            t = 0.0; boarded_total = 0; boarding_timer = 0.0
            simulation_complete = False

        if not paused and not simulation_complete:
            t += dt

            active_idx = [i for i, a in enumerate(agents) if not a.boarded]
            
            # --- AGENT STATE MACHINE & MOVEMENT ---
            for i in active_idx:
                a = agents[i]
                
                # 1. Seeking agents try to join a queue
                if a.state == 'seeking':
                    q = queues[a.queue_idx]
                    # Target the spot at the back of the line
                    a.target_pos = queue_slots[a.queue_idx][len(q)]
                    dist_sq = (a.x - a.target_pos[0])**2 + (a.y - a.target_pos[1])**2
                    if dist_sq < (QUEUE_JOIN_DISTANCE**2):
                        a.state = 'queueing'
                        a.slot_idx = len(q)
                        q.append(i)
                
                # 2. Queued agents update their target slot
                if a.state == 'queueing':
                    a.target_pos = queue_slots[a.queue_idx][a.slot_idx]

                # 3. Move agent towards its target
                if a.target_pos:
                    step = a.speed * dt
                    a.x, a.y = next_pos_with_avoid(a.x, a.y, a.target_pos[0], a.target_pos[1], step)

            resolve_agent_collisions(agents, active_idx, grid_w, grid_h)

            # --- NEW BOARDING LOGIC ---
            boarding_timer += dt
            if boarding_timer >= BOARDING_INTERVAL:
                boarding_timer -= BOARDING_INTERVAL
                for d_idx, q in enumerate(queues):
                    if len(q) >= 3:
                        # Check if the front 3 agents are in position
                        ready_to_board = True
                        for i in range(3):
                            agent = agents[q[i]]
                            slot_pos = queue_slots[d_idx][i]
                            dist_sq = (agent.x - slot_pos[0])**2 + (agent.y - slot_pos[1])**2
                            if dist_sq > (AGENT_RADIUS * 1.5)**2: # Must be close to slot
                                ready_to_board = False; break
                        
                        if ready_to_board:
                            # Board the front 3 agents
                            for _ in range(3):
                                agent_idx = q.popleft()
                                agents[agent_idx].boarded = True
                                agents[agent_idx].state = 'boarded'
                                boarded_total += 1
                            
                            # Update slot indices for all remaining agents in this queue
                            for new_slot_idx, agent_idx in enumerate(q):
                                agents[agent_idx].slot_idx = new_slot_idx

        if boarded_total >= len(agents) and not simulation_complete:
            simulation_complete = True
            effective_brate = 3.0 / BOARDING_INTERVAL if BOARDING_INTERVAL > 0 else 0
            log_simulation_results(n_pass, n_doors, mean_sp, effective_brate, t)
            print(f"Simulation complete. Dwell time: {t:.1f}s. Logged to CSV.")

        avg_queue = (sum(len(q) for q in queues) / len(queues)) if queues else 0.0

        # draw sim area
        sim_surface = screen.subsurface((0,0,SIM_W,H))
        draw_layout(sim_surface, mapper, door_x)
        draw_heatmap(sim_surface, mapper, agents)
        draw_agents(sim_surface, mapper, agents)
        draw_title(sim_surface, fonts)
        draw_stats(sim_surface, fonts, t, boarded_total, len(agents), clock.get_fps(), avg_queue)

        # draw UI
        screen.blit(panel, (SIM_W, 0))
        ui_surface = screen.subsurface((SIM_W, 0, UI_W, H))
        for s in sliders: s.draw(ui_surface, fonts.m, fonts.s)
        btn_pause.draw(ui_surface, fonts.m)
        btn_apply.draw(ui_surface, fonts.m)
        btn_reset.draw(ui_surface, fonts.m)

        pygame.display.flip()