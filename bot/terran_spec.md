# Terran Bot Specification (TODO)

## 1. Overview
This document outlines the planned implementation for the Terran race logic in the VersusAI bot. The Terran bot focuses on positional play, drops, and mechanical efficiency.

## 2. Unit Compositions
### 2.1 Bio (Marine/Marauder/Medivac)
*   **Standard**: Marine, Marauder, Medivac, Tank.
*   **Upgrades**: Stimpack, Combat Shields, Concussive Shells, +X/+X Infantry.
*   **Target Personality**: Standard, Aggressive.

### 2.2 Mech (Tank/Thor/Hellbat)
*   **Composition**: Siege Tanks, Thors, Hellbats, Vikings.
*   **Upgrades**: Armory Vehicle Weapons/Plating.
*   **Target Personality**: Economic, Defensive.

## 3. Build Orders (By Personality)
### 3.1 Economic (CC First)
*   14 Supply Depot
*   17 Command Center (Natural)
*   18 Barracks
*   19 Refinery
*   **Goal**: Secure 3 bases quickly and max out on 200 supply.

### 3.2 Aggressive (Reaper Fast Expand)
*   14 Supply Depot
*   15 Gas
*   16 Barracks
*   17 Reaper (Scout/Harass)
*   20 Command Center
*   **Goal**: Map control and early pressure.

### 3.3 Cheese (Proxy Barracks)
*   12 Supply Depot
*   13/14 Proxy Barracks x2 (Hidden location)
*   Bunker rush at enemy natural.
*   **Goal**: End game in <5 minutes.

## 4. Micro Logic
*   **Stutter Step**: Marines must shoot and move to kite Zealots/Zerglings.
*   **Siege logic**: Tanks must siege before engagement and unsiege to advance.
*   **Medivac Drop**: Load 8 marines, boost to enemy mineral line, unload, stim, attack.

## 5. Skill Level Adjustments
*   **Bronze/Silver**: No stutter step. Tanks siege late. Supply blocks frequent.
*   **Gold/Plat**: Basic stutter step. Good expansion timing.
*   **Diamond/Master**: Multi-pronged drops. Split marines against Banelings.

## 6. Implementation Plan
1.  Implement `TerranBot` class.
2.  Create `BioManager` and `MechManager`.
3.  Implement `SiegeTankManager` for positioning.
