import can
import time

def send_data(mode):
    # Enable fd=True for the bus to support CAN FD packets
    bus = can.interface.Bus(bustype='udp_multicast', channel='224.0.0.251', fd=True)

    payload = b"GPS_LAT:22.6273,LON:120.3014"
    transfer_id = 5
    extended_id = 0x10FFFF42

    print("\n==================================================")
    print(f"📡 [GPS Sensor] Mode: {mode.upper()}")
    print("⚠️  Press Ctrl+C to exit.")
    print("==================================================\n")

    try:
        while True:
            # --- CAN FD Mode Logic ---
            if mode == 'canfd':
                print(f"🚀 [CAN FD] Transmitting entire {len(payload)}-Byte payload in a SINGLE frame...")
                
                # In python-can, set is_fd=True. BRS (Bit Rate Switch) is often enabled with bitrate_switch=True
                msg = can.Message(
                    arbitration_id=extended_id,
                    data=payload,
                    is_extended_id=True,
                    is_fd=True,          # Declare FD format (FDF bit)
                    bitrate_switch=True  # Engage the "Clutch" (BRS bit)
                )
                bus.send(msg)
                print("✅ Transmission complete!\n")
            
            # --- Classic DroneCAN Mode Logic ---
            elif mode == 'dronecan':
                print(f"📡 [GPS Sensor] Preparing to fragment and transmit 28-Byte payload.")
                toggle = 0
                chunks = [payload[i:i+7] for i in range(0, len(payload), 7)]

                for i, chunk in enumerate(chunks):
                    sot = 1 if i == 0 else 0
                    eot = 1 if i == len(chunks) - 1 else 0

                    tail_byte = (sot << 7) | (eot << 6) | (toggle << 5) | (transfer_id & 0x1F)
                    data = list(chunk) + [tail_byte]

                    msg = can.Message(
                        arbitration_id=extended_id,
                        data=data,
                        is_extended_id=True,
                        is_fd=False # Classic CAN
                    )

                    bus.send(msg)
                    print(f"🚀 Tx Fragment #{i+1}: Data {chunk} | Tail: {hex(tail_byte)} (SOT:{sot} EOT:{eot} Tog:{toggle})")
                    toggle = 1 - toggle
                    time.sleep(0.5) 

                print("✅ [GPS Sensor] Full payload transmitted!\n")
            
            time.sleep(3) # Wait before next transmission cycle

    except KeyboardInterrupt:
        print("\n🛑 [GPS Sensor] Node powered off.")

if __name__ == "__main__":
    while True:
        print("\nSelect Protocol Mode:")
        print("1. Classic DroneCAN (Fragmentation Demo)")
        print("2. CAN FD (High Bandwidth Demo)")
        choice = input("Enter choice (1 or 2): ")
        
        if choice == '1':
            send_data('dronecan')
            break
        elif choice == '2':
            send_data('canfd')
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")