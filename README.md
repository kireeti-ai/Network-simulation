# Mobile Network Simulation System

This project simulates a mobile cellular network, modeling essential components like network zones, towers, and users. It demonstrates dynamic user connectivity, handovers between towers, call routing, and the ability for users to switch between different network zones.

## Features

1.  **Network Zones and Towers:**
    * Supports multiple distinct network zones.
    * Towers within each zone have specified positions, heights, and coverage areas, with non-overlapping coverage within the same zone.
2.  **User Registration and Connection Management:**
    * Users can register to a network zone and automatically connect to the nearest available tower.
    * Tracks user location and ensures connection to the most suitable tower as they move.
3.  **Dynamic User Movement & Handover:**
    * Simulates user mobility within the network.
    * Implements an automatic handover mechanism for users moving out of range of their current tower.
4.  **Call Functionality:**
    * Enables users within the same network zone to make calls to each other.
    * Call paths are routed through connected towers and a central MSC (Main Switching Center).
    * Handles cases where a call fails if a user is outside network coverage.
5.  **Network Switching:**
    * Allows users to switch between different network zones, maintaining their connection and movement history.
6.  **Error Handling and Robustness:**
    * Provides clear messages for users outside coverage or unable to connect.
    * Includes input validation for various operations.

## Design Choices

* **Graph-Based Structure:** Towers and connections within a network are modeled as a graph, enabling efficient pathfinding for call routing and handover management.
* **Distance Calculations & Radius Checks:** Used to determine proximity for tower connections, ensure non-overlapping tower coverage, and manage user movement and handovers.
* **Hash Map for Users:** A custom `TelephoneHashMap` is used for quick lookup and management of registered users.

## How to Run

1.  Clone the repository:
    ```bash
    git clone [https://github.com/your-username/mobile-network-simulation.git](https://github.com/your-username/mobile-network-simulation.git)
    ```
2.  Navigate to the project directory:
    ```bash
    cd mobile-network-simulation
    ```
3.  Run the main simulation script:
    ```bash
    python main.py
    ```

