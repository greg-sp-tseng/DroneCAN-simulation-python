# The Hardware Nervous System: DroneCAN & CAN FD Simulation

This repository demonstrates a software-based simulation of hardware network behavior, specifically focusing on the transition from **Classic DroneCAN (CAN 2.0B)** to **CAN FD (Flexible Data-Rate)**. It also features a **Chaos Engineering** experiment simulating hardware-level Error Frame Bombardment.

## 🚀 Project Overview

When validating hardware communication protocols, engineers often face constraints with OS-level Virtual CAN interfaces (like `vcan0` on WSL or Windows). 
This project overcomes this limitation by utilizing `python-can`'s **UDP Multicast** interface. This approach allows independent terminal processes to act as isolated physical Microcontroller Units (MCUs), effectively bypassing kernel restrictions while maintaining accurate protocol logic.

### Key Features
1. **Classic DroneCAN Simulation:** Implements manual payload fragmentation (7-Byte data + 1-Byte Tail) to transmit a 28-Byte GPS payload over an 8-Byte network constraint. Features a bitwise state machine for reassembly.
2. **CAN FD Upgrade:** Demonstrates high-bandwidth efficiency by transmitting the entire 28-Byte payload in a single frame using `FDF` and `BRS` flags, eliminating fragmentation overhead.
3. **Physical Layer (PHY) Chaos Simulation:** Introduces a "Legacy Jammer" node that intentionally crashes the bus upon detecting unknown CAN FD frames, simulating a real-world Form Error and subsequent Bus Lockup.

## 🛠️ Prerequisites

Ensure you have Python installed, along with the required dependencies:
   ```bash
   # Create and activate a virtual environment (Recommended)
   python3 -m venv .venv
   source .venv/bin/activate

   # Install required packages
   pip install python-can msgpack
   ```

## 🎬 How to Run the Simulation
This simulation requires running multiple scripts in separate terminal windows (all within the same virtual environment) to represent different hardware nodes.

Phase 1: Normal Operation (Classic vs. CAN FD)
   1. Start the Flight Controller (Terminal 1):

   ```bash
   python flight_controller.py
   ```
   Select Mode 1 (DroneCAN) or Mode 2 (CAN FD).

   2. Start the Sensor Node (Terminal 2):

   ```bash
   python sensor_node.py
   ```
   Select the matching protocol mode to observe successful transmission and reassembly.

Phase 2: Chaos Engineering (Bus Jamming)
   1. Start the Flight Controller (Terminal 1): Set to Mode 2 (CAN FD).

   2. Start the Legacy Jammer (Terminal 2): 

   ```bash
   python legacy_gps_jammer.py
   ```

   *This node acts as an old, non-FD-compliant device.*

   3. Start the Sensor Node (Terminal 3): Set to Mode 2 (CAN FD).

Observation: As soon as the Sensor Node transmits a CAN FD frame, the Jammer panics and floods the network with high-priority dominant bits (simulated via ID 0x0000001). The Flight Controller will detect this collision and drop the corrupted frame. Terminating the Jammer script instantly restores the network, mirroring the self-healing nature of hardware CAN controllers.

🧠 Engineering Takeaways
1. Transport vs. Physical Layer: UDP simulates packet-based transmission, but real CAN controllers operate on a bit-wise, destructive physical layer.
2. Fault Confinement: Real CAN hardware uses Transmit/Receive Error Counters (TEC/REC) to automatically push faulty nodes into "Bus Off" states. This simulation artificially replicates that recovery behavior.
