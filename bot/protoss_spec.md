# Protoss Bot Specification (TODO)

## 1. Overview
This document outlines the planned implementation for the Protoss race logic in the VersusAI bot. The Protoss bot focuses on powerful units, spellcasting, and timing attacks.

## 2. Unit Compositions
### 2.1 Gateway Man (Zealot/Stalker/Sentry)
*   **Composition**: Zealots (Charge), Stalkers (Blink), Sentries (Guardian Shield).
*   **Support**: Immortals or Colossi.
*   **Target Personality**: Aggressive, Timing.

### 2.2 SkyToss (Carrier/Void Ray)
*   **Composition**: Carriers, Void Rays, Mothership.
*   **Early Game**: Stargate openers (Oracle/Phoenix).
*   **Target Personality**: Economic.

## 3. Build Orders (By Personality)
### 3.1 Economic (Nexus First)
*   14 Pylon
*   17 Nexus (Natural)
*   17 Gateway
*   18 Gas
*   **Goal**: Maximize probe production. Risky against Zerg 12 pool.

### 3.2 Aggressive (4 Gate)
*   Standard Cyber Core opener.
*   Cut probes at ~22.
*   Add 3 Gateways.
*   Warp in Stalkers/Zealots at proxy pylon.
*   **Goal**: Overwhelm opponent early.

### 3.3 Cheese (Cannon Rush)
*   13 Forge.
*   Probe moves to enemy base.
*   Build Pylon + Cannons behind mineral line.
*   **Goal**: Deny mining or kill main Nexus.

## 4. Micro Logic
*   **Blink Micro**: Stalkers blink back when shield is low.
*   **Forcefields**: Sentries block ramps or split enemy armies.
*   **Oracle**: Activate beam, kill workers, deactivate/flee when energy low or threatened.

## 5. Skill Level Adjustments
*   **Bronze/Silver**: No blink micro. Slow warp-in cycles. Floating minerals.
*   **Gold/Plat**: Use of Guardian Shield. Consistent probe production.
*   **Diamond/Master**: Perfect blink micro. Storm dodging. Oracle worker harass.

## 6. Implementation Plan
1.  Implement `ProtossBot` class.
2.  Create `GatewayManager` and `TechManager`.
3.  Implement `SpellCasterManager` (High Templar/Sentry).
