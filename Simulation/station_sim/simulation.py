import sys, random, pygame
from .config import *
from .coords import ScreenMapper
from .layout import make_doors
from .spawn import spawn_agents
from .physics import next_pos_with_avoid, resolve_agent_collisions
from .render import draw_layout, draw_agents, draw_heatmap, draw_stats, draw_title, Fonts, draw_queue_slots
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

    n_pass  = int(sliders[0].value)
    n_doors = int(sliders[1].value)
    mean_sp = float(sliders[2].value)
    board_rate_setting = float(sliders[3].value)
    max_q_rows = int(sliders[4].value)
    wait_time = int(sliders[5].value) # Read new slider
    BOARDING_INTERVAL = 3.0 / board_rate_setting if board_rate_setting > 0 else float('inf')

    def reset_simulation():
        nonlocal agents, queue_slots, door_x, t, boarded_total, boarding_timer, simulation_complete, slot_occupants, boarding_allowed
        door_x = make_doors(n_doors)
        agents = spawn_agents(n_pass, door_x, mean_sp)
        
        slot_spacing_y = AGENT_RADIUS * QUEUE_SPACING_Y_FACTOR
        slot_spacing_x = AGENT_RADIUS * QUEUE_SPACING_X_FACTOR
        start_y_m = PLAT_Y0 + QUEUE_START_Y_OFFSET
        num_rows = min((n_pass // 3) + 5, max_q_rows) 
        queue_slots = [[[(dx + (j - 1) * slot_spacing_x, start_y_m + i * slot_spacing_y) for j in range(3)] for i in range(num_rows)] for dx in door_x]
        slot_occupants = [[[None for _ in range(3)] for _ in range(num_rows)] for _ in door_x]

        if door_x:
            for agent in agents:
                d_idx = min(range(len(door_x)), key=lambda k: abs(agent.target - door_x[k]))
                agent.queue_idx = d_idx
                agent.state = 'seeking'
        
        t = 0.0; boarded_total = 0; boarding_timer = 0.0
        simulation_complete = False
        boarding_allowed = False # Doors start closed

    agents, queue_slots, door_x, t, boarded_total, boarding_timer, simulation_complete, slot_occupants, boarding_allowed = [None] * 9
    reset_simulation()
    
    grid_w, grid_h = int(LENGTH_M / CELL_SIZE) + 2, int(PLAT_Y1 / CELL_SIZE) + 2

    while True:
        dt = min(clock.tick(60) / 1000.0, DT_CAP)

        btn_pause.clicked, btn_apply.clicked, btn_reset.clicked = False, False, False
        for ev in pygame.event.get():
            # ... (event handling code is the same) ...
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_q)): pygame.quit(); sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE: paused = not paused
                if ev.key == pygame.K_r: btn_reset.clicked = True
            panel_local = None
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if SIM_W <= ev.pos[0] < SIM_W + UI_W: panel_local = (ev.pos[0] - SIM_W, ev.pos[1])
            for s in sliders: s.handle(ev, panel_local)
            for b in [btn_pause, btn_apply, btn_reset]: b.handle(ev, panel_local)
        
        if btn_pause.clicked: paused = not paused
        if btn_apply.clicked:
            n_pass, n_doors, mean_sp = int(sliders[0].value), int(sliders[1].value), float(sliders[2].value)
            board_rate_setting = float(sliders[3].value)
            max_q_rows = int(sliders[4].value)
            wait_time = int(sliders[5].value) # Read new slider on Apply
            BOARDING_INTERVAL = 3.0 / board_rate_setting if board_rate_setting > 0 else float('inf')
            btn_reset.clicked = True
        if btn_reset.clicked: reset_simulation()

        if not paused and not simulation_complete:
            t += dt
            
            # --- NEW: Check if wait time is over to open doors ---
            if not boarding_allowed and t >= wait_time:
                boarding_allowed = True

            active_idx = [i for i, a in enumerate(agents) if not a.boarded]
            # ... (agent seeking and movement logic is the same) ...
            for i in active_idx:
                a=agents[i]
                if a.state == 'seeking':
                    d_idx = a.queue_idx
                    if d_idx < len(slot_occupants):
                        for r, row in enumerate(slot_occupants[d_idx]):
                            for c, occ in enumerate(row):
                                if occ is None: a.slot_row, a.slot_col, a.state = r, c, 'queueing'; slot_occupants[d_idx][r][c] = i; break
                            if a.state=='queueing': break
                if a.state=='queueing': a.target_pos=queue_slots[a.queue_idx][a.slot_row][a.slot_col]
                if a.target_pos: a.x, a.y = next_pos_with_avoid(a.x,a.y,a.target_pos[0],a.target_pos[1],a.speed*dt)

            resolve_agent_collisions(agents, active_idx, grid_w, grid_h)
            
            # --- MODIFIED: Boarding is only possible if doors are open ---
            if boarding_allowed:
                boarding_timer += dt
                if boarding_timer >= BOARDING_INTERVAL:
                    boarding_timer -= BOARDING_INTERVAL
                    # ... (boarding and shuffling logic is the same as before) ...
                    for d_idx in range(n_doors):
                        if not slot_occupants or d_idx >= len(slot_occupants) or not slot_occupants[d_idx]: continue
                        front_row_indices = [slot_occupants[d_idx][0][c] for c in range(3) if slot_occupants[d_idx][0][c] is not None]
                        agents_behind = any(slot_occupants[d_idx][r][c] is not None for r in range(1,len(slot_occupants[d_idx])) for c in range(3))
                        can_board_full = len(front_row_indices) == 3
                        can_board_remnants = len(front_row_indices) > 0 and not agents_behind
                        if can_board_full or can_board_remnants:
                            front_agents = [agents[i] for i in front_row_indices]
                            if all((a.x-a.target_pos[0])**2+(a.y-a.target_pos[1])**2<(AGENT_RADIUS*1.5)**2 for a in front_agents):
                                for agent in front_agents: agent.boarded=True; boarded_total+=1
                                if len(front_agents)==3:
                                    for r in range(len(slot_occupants[d_idx])-1): slot_occupants[d_idx][r] = slot_occupants[d_idx][r+1]
                                    slot_occupants[d_idx][-1] = [None,None,None]
                                    for agent in agents:
                                        if not agent.boarded and agent.queue_idx==d_idx and agent.state=='queueing': agent.slot_row-=1
                                else:
                                    for c in range(3):
                                        if slot_occupants[d_idx][0][c] in front_row_indices: slot_occupants[d_idx][0][c]=None

            if boarded_total >= n_pass and not simulation_complete:
                simulation_complete = True
                log_simulation_results(n_pass, n_doors, mean_sp, 3.0/BOARDING_INTERVAL if BOARDING_INTERVAL > 0 else 0, t)

        avg_queue = sum(1 for a in agents if a.state == 'queueing') / n_doors if n_doors > 0 else 0.0
        
        sim_surface = screen.subsurface((0,0,SIM_W,H))
        # --- MODIFIED: Pass boarding_allowed status to the renderer ---
        draw_layout(sim_surface, mapper, door_x, boarding_allowed)
        draw_queue_slots(sim_surface, mapper, queue_slots)
        draw_heatmap(sim_surface, mapper, agents)
        draw_agents(sim_surface, mapper, agents)
        draw_title(sim_surface, fonts)
        draw_stats(sim_surface, fonts, t, boarded_total, n_pass, clock.get_fps(), avg_queue)
        
        screen.blit(panel, (SIM_W, 0))
        ui_surface = screen.subsurface((SIM_W, 0, UI_W, H))
        for s in sliders: s.draw(ui_surface, fonts.m, fonts.s)
        for b in [btn_pause, btn_apply, btn_reset]: b.draw(ui_surface, fonts.m)
        pygame.display.flip()