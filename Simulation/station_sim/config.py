# World config (meters, seconds)
LENGTH_M   = 100.0
PLAT_Y0    = 0.0
PLAT_Y1    = 6.0
SAFETY_Y   = 0.8

# Initial parameters (overridden by UI)
INIT_PASS   = 70
INIT_DOORS  = 6
INIT_SPEED  = 1.2     # mean walking speed (m/s)
INIT_BOARD  = 1.6     # pax/s/door
BOARD_ZONE  = 0.22    # m around door line where boarding can occur (legacy)
QUEUE_JOIN_DISTANCE = 1.0 # m, how close to get to back of queue to join it
QUEUE_SLOT_COLOR = (210, 210, 210) # A light grey for the queue markers

DT_CAP       = 1/60
AGENT_RADIUS = 0.25
CELL_SIZE    = 1.0

# Screen & UI (pixels)
W, H = 1280, 620
UI_W = 320
SIM_W = W - UI_W

# World-to-screen vertical window (meters)
Y_MIN, Y_MAX = -1.5, 7.5

INIT_Q_ROWS = 10      # Default number of queue rows (x3 slots)

# (Add these constants to your existing config.py file)

# --- Queue Layout Parameters ---
QUEUE_SPACING_Y_FACTOR = 1.0  # Vertical spacing between rows (as a multiplier of agent radius)
QUEUE_SPACING_X_FACTOR = 3.5  # Horizontal spacing between slots (as a multiplier of agent radius)
QUEUE_START_Y_OFFSET = 1.0    # How far from the platform edge the first row starts (in meters)


INIT_WAIT_TIME = 5      # Default seconds to wait before doors open and boarding starts

# --- Colors ---
DOOR_COLOR_CLOSED = (200, 50, 50) # Red
DOOR_COLOR_OPEN = (50, 200, 50)   # Green