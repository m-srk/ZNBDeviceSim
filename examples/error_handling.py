"""
Example: Error handling in ZNBDeviceSim

This example demonstrates common error scenarios and how to handle them.
"""

from ZonedNBDevice import ZonedNBDevice


def main():
    zbd = ZonedNBDevice(nzones=2, zonesize=16)
    
    print("--- Error Handling Examples ---\n")
    
    # Example 1: Writing not at write pointer
    print("1. Attempting to write not at write pointer...")
    try:
        zbd.write_rock(1000, 100, bytearray(100))
    except Exception as e:
        print(f"   ✗ Error caught: {e}\n")
    
    # Example 2: Reading non-existent rock
    print("2. Attempting to read non-existent rock...")
    try:
        dest = bytearray(100)
        zbd.read_rock(5000, 100, dest)
    except Exception as e:
        print(f"   ✗ Error caught: {e}\n")
    
    # Example 3: Writing beyond zone capacity
    print("3. Attempting to write beyond zone capacity...")
    zone_size = 16 * 1024 * 1024  # 16MB
    try:
        zbd.write_rock(0, zone_size + 1, bytearray(zone_size + 1))
    except Exception as e:
        print(f"   ✗ Error caught: {e}\n")
    
    # Example 4: Reading with wrong size
    print("4. Writing a rock, then reading with wrong size...")
    data = bytearray(b"Test data")
    zbd.write_rock(0, len(data), data)
    try:
        dest = bytearray(100)  # Wrong size
        zbd.read_rock(0, 100, dest)
    except Exception as e:
        print(f"   ✗ Error caught: {e}\n")
    
    # Example 5: Correct usage
    print("5. Correct usage - sequential writes...")
    zbd.reset_zone(zoneid=0)
    
    wptr = zbd.write_rock(0, 512, bytearray(512))
    print(f"   ✓ Wrote 512 bytes, wptr = {wptr}")
    
    wptr = zbd.write_rock(512, 256, bytearray(256))
    print(f"   ✓ Wrote 256 bytes, wptr = {wptr}")
    
    print("\n--- Error Handling Complete ---")


if __name__ == "__main__":
    main()
