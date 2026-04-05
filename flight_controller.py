import can
import time

def receive_multiframe(mode):
    bus = can.interface.Bus(bustype='udp_multicast', channel='224.0.0.251')
    
    print("\n==================================================")
    print(f"🎧 [Flight Controller] Mode: {mode.upper()}")
    print("Listening on CAN over UDP (Multicast Channel 224.0.0.251)...")
    print("⚠️  Press Ctrl+C to exit.")
    print("==================================================\n")

    reassembly_buffer = {}
    ERROR_FRAME_ID = 0x0000001 # The ID our Jammer uses

    try:
        while True:
            msg = bus.recv(timeout=1.0)
            if msg is None:
                continue

            # --- Physical Layer Simulation: Detect Bus Jamming ---
            if msg.arbitration_id == ERROR_FRAME_ID:
                print("💥 [PHY Sim] BUS ERROR! Voltage levels corrupted by Error Frame.")
                continue

            # --- CAN FD Mode Logic ---
            if mode == 'canfd':
                if msg.is_fd:
                    # 🌟 Simulation Magic: Wait 100ms to see if anyone screams "Error!"
                    # In reality, this happens bit-by-bit in microseconds.
                    collision = False
                    start_time = time.time()
                    
                    while time.time() - start_time < 0.1:
                        check_msg = bus.recv(timeout=0.01)
                        if check_msg and check_msg.arbitration_id == ERROR_FRAME_ID:
                            collision = True
                            break
                    
                    if collision:
                        print("❌ [Flight Controller] Frame destroyed during transmission! (Simulated Bus Lockup)")
                    else:
                        payload = msg.data
                        print(f"📥 [CAN FD] Single Frame Rx ({len(payload)} Bytes): {bytes(payload).decode('utf-8')}")
                else:
                    continue
            
            # --- Classic DroneCAN Mode Logic ---
            elif mode == 'dronecan':
                if msg.is_fd:
                    continue 

                tail_byte = msg.data[-1]
                sot = (tail_byte >> 7) & 1
                eot = (tail_byte >> 6) & 1
                toggle = (tail_byte >> 5) & 1
                transfer_id = tail_byte & 0x1F
                
                payload_chunk = msg.data[:-1]

                print(f"📥 Rx Fragment -> Chunk: {bytes(payload_chunk).ljust(7, b' ')} | Tail -> SOT:{sot} EOT:{eot} Tog:{toggle} TID:{transfer_id}")

                if sot == 1:
                    reassembly_buffer[transfer_id] = {
                        'data': bytearray(payload_chunk),
                        'expected_toggle': 1 - toggle 
                    }
                else:
                    if transfer_id in reassembly_buffer:
                        state = reassembly_buffer[transfer_id]
                        if toggle == state['expected_toggle']:
                            state['data'].extend(payload_chunk)
                            state['expected_toggle'] = 1 - toggle
                        else:
                            print(f"⚠️ [WARNING] Toggle mismatch! Discarding payload.")
                            del reassembly_buffer[transfer_id]
                            continue

                if eot == 1 and transfer_id in reassembly_buffer:
                    complete_data = reassembly_buffer[transfer_id]['data']
                    print(f"\n🎉 [Flight Controller] Reassembly successful! Decoded: {bytes(complete_data).decode('utf-8')}\n")
                    del reassembly_buffer[transfer_id] 

    except KeyboardInterrupt:
        print("\n🛑 [Flight Controller] Shutting down listener.")

if __name__ == "__main__":
    while True:
        print("\nSelect Protocol Mode:")
        print("1. Classic DroneCAN (Fragmentation Demo)")
        print("2. CAN FD (High Bandwidth Demo)")
        choice = input("Enter choice (1 or 2): ")
        
        if choice == '1':
            receive_multiframe('dronecan')
            break
        elif choice == '2':
            receive_multiframe('canfd')
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")