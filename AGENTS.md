# AGENTS.md: StarCraft 2 Bot Architecture & Development Standards

## 1. Executive Summary
This document defines the technical standards for the "VersusAI" StarCraft 2 Bot. The project aims to provide a human-competing AI capable of playing all three races (Zerg, Terran, Protoss) with configurable skill levels and personalities.

### Core Technology Stack
| Component | Technology | Justification |
| :--- | :--- | :--- |
| **Framework** | `python-sc2` | Standard, high-performance Python wrapper for the SC2 Client API. |
| **Runtime** | Python 3.8+ | Compatible with `python-sc2` and standard environments. |
| **GUI** | `tkinter` | Native, lightweight GUI for the game launcher/configurator. |
| **Distribution** | `PyInstaller` | Bundles the Python environment and bot into a standalone Windows Executable. |

---

## 2. Architectural Patterns

### 2.1 Bot Logic Structure
The bot does **not** use an Event-Driven LangGraph. Instead, it follows the standard `python-sc2` step-loop architecture:
*   **`on_step(iteration)`**: The main game loop running approx. 22.4 times per game second (faster in simulation).
*   **Managers**: Logic is divided into managers (e.g., `EconomyManager`, `ArmyManager`, `BuildManager`) to keep `on_step` clean.
*   **Skill & Personality**:
    *   **SkillManager**: Throttles APM and injects decision errors based on the configured MMR/Tier.
    *   **PersonalityManager**: Dictates the high-level strategy (Build Order, Aggression Level).

### 2.2 Configuration & State
*   Configuration is passed via Command Line Arguments (CLI) from the Launcher to the Bot process.
*   The Bot must be stateless between games (fresh start).

---

## 3. Feature Specifications

### 3.1 Adaptive Skill Level
The bot must simulate human ladder tiers:
*   **Bronze - Gold**: Low APM, missed macro cycles (injects/mules), supply blocks, poor micro.
*   **Platinum - Diamond**: Decent macro, basic micro, standard builds.
*   **Master - GM (9999 MMR)**: "Unrestricted/Best Effort". Max APM, tight builds, frame-perfect micro (where possible).

### 3.2 Personality Profiles
*   **Economic**: Focus on drone count, bases, and late-game tech.
*   **Aggressive**: Early attacks, pressure units (Zerglings, Reapers, Adepts).
*   **Cheese**: All-in strategies (12 Pool, Proxy Barracks, Cannon Rush).
*   **Timing**: Hitting specific power spikes (e.g., +1/+1 Upgrades).

---

## 4. Development Guidelines

### 4.1 Resource Optimization
*   Avoid memory leaks. Clear lists/dicts that grow indefinitely.
*   Use standard Python data structures efficiently.
*   Do not block the `on_step` loop for more than 10-20ms to avoid lag.

### 4.2 Code Organization
*   `bot/`: Contains all bot logic.
*   `launcher.py`: The GUI entry point.
*   `run.py`: The CLI entry point for the bot process.
