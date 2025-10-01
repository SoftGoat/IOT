# Train Station Simulator

A Python-based simulation project using Pygame to model the design, queueing, and passenger flow within a train station platform.

## 1. Project Architecture Overview

This project follows the **State Machine Design Pattern** combined with **Object-Oriented Programming (OOP)** principles to achieve separation of concerns.

### 1.1 Core Components

| Component | Responsibility | Details |
| :--- | :--- | :--- |
| **`main.py`** | **State Machine Driver** | Initializes Pygame and contains the main game loop. It manages the current game state and delegates event handling, updates, and drawing to the active state object. |
| **`config.py`** | **Global Configuration** | Stores all global constants, file paths, colors, screen dimensions, font sizes, and tile mappings. |
| **`game_states/`** | **Game States** | A package containing classes that define the behavior for each major screen/mode of the game (e.g., `MainMenu`, `BuildState`, `SimulationState`). |
| **`ui_elements.py`** | **Reusable UI** | Contains fundamental UI components like `Button` and `TileButton`. Uses the **Callback Pattern** to decouple button aesthetics from button actions. |
| **`dialogs.py`** | **Modal UI** | Implements complex, modal user interfaces like `LoadDialog` and `SaveDialog`, which interrupt the main game loop until resolved. |

### 1.2 State Machine Pattern

All classes that represent a major screen or mode (e.g., `MainMenu`, `BuildState`, `SimulationState`) inherit from the **`State`** class.

* **`State.handle_events(events)`**: Processes user input (mouse, keyboard).
* **`State.update()`**: Runs game logic (timers, hover checks).
* **`State.draw(screen)`**: Renders all visual elements to the screen.

When a state is finished, it sets `self.done = True` and `self.next_state` to the name of the next state (e.g., `"SIMULATION"`), triggering the transition in `main.py`.

### 1.3 Key Utility Modules

* **`game_states/layout_io.py`**: Handles all file persistence operations (JSON encoding/decoding) for loading and saving grid layouts.
* **`game_states/tile_manager.py`**: Manages the visual representation of the station grid, handling image loading, scaling, and sprite group management.

---

## 2. Setup and Execution

### 2.1 Prerequisites

This project requires Python 3.x and the Pygame library.

1.  **Install Python:** Ensure Python 3.8+ is installed on your system.
2.  **Install Pygame:** Use pip to install the recommended version of Pygame.

```bash
pip install pygame-ce

## <span style="color:blue">2. Setup and Execution</span>
    Documentation:
    This section provides instructions for running the main simulation script of the Train Station Simulator project.
    - Ensure you are in the project's root directory.
    - Execute the main Python script (`main.py`) using Python 3.
    - The command to run is: `python3 main.py`
    This will start the simulation as defined in the project.
-->
Navigate to the project's root directory (Train Station Simulator/).

Run the main script using Python:

Bash

python3 main.py