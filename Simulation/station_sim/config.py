# World config (meters, seconds)
LENGTH_M   = 100.0
PLAT_Y0    = 0.0
PLAT_Y1    = 6.0
SAFETY_Y   = 0.8

# Initial parameters (overridden by UI)
INIT_PASS   = 240
INIT_DOORS  = 6
INIT_SPEED  = 1.2     # mean walking speed (m/s)
INIT_BOARD  = 1.6     # pax/s/door
BOARD_ZONE  = 0.22    # m around door line where boarding can occur (legacy)
QUEUE_JOIN_DISTANCE = 1.0 # m, how close to get to back of queue to join it

DT_CAP       = 1/60
AGENT_RADIUS = 0.25
CELL_SIZE    = 1.0

# Screen & UI (pixels)
W, H = 1280, 620
UI_W = 320
SIM_W = W - UI_W

# World-to-screen vertical window (meters)
Y_MIN, Y_MAX = -1.5, 7.5