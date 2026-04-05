import can
import time

def run_legacy_jammer():
    # Bind to the same multicast IP
    bus = can.interface.Bus(bustype='udp_multicast', channel='224.0.0.251')
    
    print("\n==================================================")
    print("😈 [Legacy GPS Node] Mode: CLASSIC (FD Intolerant)")
    print("Simulating an old node that panics when it sees CAN FD frames.")
    print("⚠️  Press Ctrl+C to exit.")
    print("==================================================\n")

    # A very high priority ID (low number) to simulate an Error Frame overriding others
    error_frame_id = 0x0000001 
    
    try:
        while True:
            # Listen to the network
            msg = bus.recv(timeout=1.0)
            if msg is None:
                continue
            
            # The Trigger: If it sees a CAN FD frame, it panics!
            if msg.is_fd:
                print(f"💥 [Legacy GPS] PANIC! Detected unknown FD format (FDF=1). Initiating Error Frame Bombardment!")
                
                # Simulate Error Frame: Flood the bus with high-priority classic frames
                for _ in range(50): 
                    error_msg = can.Message(
                        arbitration_id=error_frame_id,
                        data=[0x00]*8, # 8 bytes of zeros (dominant bits)
                        is_extended_id=False,
                        is_fd=False
                    )
                    bus.send(error_msg)
                    # Very short delay to simulate flooding
                    time.sleep(0.01)
                
                print("🛑 [Legacy GPS] Network jammed temporarily.\n")

    except KeyboardInterrupt:
        print("\n🛑 [Legacy GPS] Powered off.")

if __name__ == "__main__":
    run_legacy_jammer()