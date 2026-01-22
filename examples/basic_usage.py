"""
Example: Basic usage of ZNBDeviceSim

This example demonstrates:
1. Creating a zoned device
2. Writing multiple rocks sequentially
3. Reading rocks back
4. Resetting a zone for reuse
"""

from ZonedNBDevice import ZonedNBDevice


def main():
    # Create a device with 3 zones, each 32MB
    print("Creating ZNB device with 3 zones of 32MB each...")
    zbd = ZonedNBDevice(nzones=3, zonesize=32)
    
    # Write some rocks
    print("\n--- Writing Rocks ---")
    
    # Rock 1: Small text data
    data1 = bytearray(b"Hello, ZNB World!")
    wptr = zbd.write_rock(0, len(data1), data1)
    print(f"Wrote rock 1 ({len(data1)} bytes) at address 0, write pointer now at {wptr}")
    
    # Rock 2: Larger data
    data2 = bytearray(b"X" * 4096)  # 4KB of data
    wptr = zbd.write_rock(wptr, len(data2), data2)
    print(f"Wrote rock 2 ({len(data2)} bytes), write pointer now at {wptr}")
    
    # Rock 3: Another small rock
    data3 = bytearray(b"Sequential writes are enforced!")
    wptr = zbd.write_rock(wptr, len(data3), data3)
    print(f"Wrote rock 3 ({len(data3)} bytes), write pointer now at {wptr}")
    
    # Read rocks back
    print("\n--- Reading Rocks ---")
    
    dest1 = bytearray(len(data1))
    zbd.read_rock(0, len(data1), dest1)
    print(f"Read rock 1: {dest1.decode()}")
    
    dest3 = bytearray(len(data3))
    zbd.read_rock(wptr - len(data3), len(data3), dest3)
    print(f"Read rock 3: {dest3.decode()}")
    
    # Reset zone and reuse
    print("\n--- Resetting Zone ---")
    zbd.reset_zone(zoneid=0)
    print("Zone 0 reset, can now write from beginning again")
    
    # Write new data after reset
    new_data = bytearray(b"Fresh start after reset!")
    wptr = zbd.write_rock(0, len(new_data), new_data)
    print(f"Wrote new rock at address 0, write pointer at {wptr}")
    
    dest_new = bytearray(len(new_data))
    zbd.read_rock(0, len(new_data), dest_new)
    print(f"Read new rock: {dest_new.decode()}")
    
    print("\n--- Example Complete ---")


if __name__ == "__main__":
    main()
