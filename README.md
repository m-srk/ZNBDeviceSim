# ZNBDeviceSim

[![Tests](https://github.com/m-srk/ZNBDeviceSim/workflows/Tests/badge.svg)](https://github.com/m-srk/ZNBDeviceSim/actions)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python-based simulator for Zoned Null Block (ZNB) devices with support for zone-based sequential write operations and rock (data object) management.

## Overview

ZNBDeviceSim provides a software implementation of a Zoned Null Block device, which mimics the behavior of zoned storage devices (like ZNS SSDs). The simulator enforces sequential write constraints within zones and provides an interface for reading and writing "rocks" (data objects) to pages backed by the zoned device.

## Features

- **Zone-based Storage**: Configurable number of zones with customizable zone sizes
- **Sequential Write Enforcement**: Maintains write pointers per zone to ensure sequential writes
- **Page-level Management**: 4KB page granularity with allocation tracking
- **Rock Interface**: High-level API for storing and retrieving data objects
- **Zone Reset**: Support for resetting zones to reclaim space
- **Detailed Logging**: Built-in debug logging for operations

## Architecture

### Key Concepts

- **Zone**: A contiguous region of storage with a write pointer that advances sequentially
- **Rock**: A data object stored in the device, tracked by start address and size
- **Page**: 4KB storage unit, the smallest allocation granularity
- **Write Pointer**: Per-zone pointer indicating the next writable location

## Installation

### From Source

```bash
git clone https://github.com/m-srk/ZNBDeviceSim.git
cd ZNBDeviceSim
pip install -r requirements.txt
```

### Prerequisites

- Python 3.7+
- `sortedcontainers` library (installed automatically)

## Usage

### Basic Example

```python
from ZonedNBDevice import ZonedNBDevice

# Create a device with 5 zones, each 64MB
zbd = ZonedNBDevice(nzones=5, zonesize=64)

# Write a rock (data object)
data = bytearray(b"Hello, World!")
write_ptr = zbd.write_rock(saddr=0, nbytes=len(data), src=data)
print(f"Write pointer after write: {write_ptr}")

# Read the rock back
dest = bytearray(len(data))
zbd.read_rock(saddr=0, nbytes=len(data), dest=dest)
print(f"Read data: {dest.decode()}")

# Reset zone to reclaim space
zbd.reset_zone(zoneid=0)
```

### API Reference

#### ZonedNBDevice

**Constructor**
```python
ZonedNBDevice(nzones: int, zonesize: int)
```
- `nzones`: Number of zones in the device
- `zonesize`: Size of each zone in MB

**Methods**

```python
write_rock(saddr: int, nbytes: int, src: bytearray) -> int
```
Writes a rock to the device starting at the specified address.
- `saddr`: Start address (must match zone's write pointer)
- `nbytes`: Number of bytes to write
- `src`: Source buffer containing data
- Returns: Updated write pointer
- Raises: Exception if address doesn't match write pointer or insufficient space

```python
read_rock(saddr: int, nbytes: int, dest: bytearray)
```
Reads a rock from the device.
- `saddr`: Start address of the rock
- `nbytes`: Number of bytes to read (must match rock size)
- `dest`: Destination buffer (must be same size as nbytes)
- Raises: Exception if rock doesn't exist or size mismatch

```python
reset_zone(staddr: int = -1, zoneid: int = -1)
```
Resets a zone, moving write pointer back to start and deallocating pages.
- `staddr`: Start address within the zone to reset
- `zoneid`: Zone ID to reset
- Note: Provide either `staddr` or `zoneid`

```python
get_zone(addr: int) -> Zone
```
Returns the zone object containing the given address.

## Constraints and Behavior

### Sequential Write Requirement
- Writes must occur at the zone's current write pointer
- Writing to any other address within a zone will raise an exception
- This mimics real zoned storage device behavior

### Zone Boundaries
- Writes cannot span multiple zones
- Reads cannot span multiple zones
- Each zone must be managed independently

### Rock Management
- Rocks are tracked at the page level
- A rock's start address must be at a previously written location
- Reading requires exact size match with the original rock

### Page Allocation
- Pages are 4KB in size
- Pages are allocated on-demand during writes
- Pages can be deallocated via zone reset

## Example Scenarios

### Writing Multiple Rocks

```python
zbd = ZonedNBDevice(5, 64)

# Write first rock
wptr = zbd.write_rock(0, 1024, bytearray(1024))
print(f"Write pointer: {wptr}")  # Output: 1024

# Write second rock (must start at current write pointer)
wptr = zbd.write_rock(1024, 512, bytearray(b"A" * 512))
print(f"Write pointer: {wptr}")  # Output: 1536
```

### Zone Reset and Reuse

```python
# Fill zone with data
zbd.write_rock(0, 1024, bytearray(1024))
zbd.write_rock(1024, 2048, bytearray(2048))

# Reset zone to reclaim space
zbd.reset_zone(zoneid=0)

# Can now write from beginning again
zbd.write_rock(0, 512, bytearray(512))
```

### Error Handling

```python
try:
    # This will fail - not at write pointer
    zbd.write_rock(5000, 100, bytearray(100))
except Exception as e:
    print(f"Error: {e}")  # "Address does not match write ptr"

try:
    # This will fail - rock doesn't exist
    dest = bytearray(100)
    zbd.read_rock(99999, 100, dest)
except Exception as e:
    print(f"Error: {e}")  # "No rock exists at given address !"
```

## Examples

Check the `examples/` directory for more usage scenarios:
- `basic_usage.py` - Basic operations and zone reset
- `error_handling.py` - Common error scenarios and handling

Run examples:
```bash
PYTHONPATH=. python examples/basic_usage.py
PYTHONPATH=. python examples/error_handling.py
```

## Testing

### Run Unit Tests

```bash
# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install sortedcontainers

# Run tests
python -m unittest test_ZonedNBDevice -v
```

### Run Demo

```bash
python ZonedNBDevice.py
```

This executes a series of write and read operations to demonstrate functionality.

## Limitations

- In-memory only (no persistence)
- Single-threaded (no concurrency support)
- Fixed 4KB page size
- All zones must be the same size

## Use Cases

- Testing zoned storage applications without hardware
- Educational tool for understanding zoned storage concepts
- Prototyping zone-aware data structures and algorithms
- Simulating ZNS SSD behavior in software

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

**Srikanth Mantravadi**  
Email: mantravadisrikanth@gmail.com

## License

MIT License

Copyright (c) 2026 Srikanth Mantravadi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## References

- [ZNS (Zoned Namespaces) Specification](https://zonedstorage.io/)
- [Linux Zoned Block Device Support](https://www.kernel.org/doc/html/latest/block/zoned.html)
