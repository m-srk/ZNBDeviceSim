"""
Unit tests for ZonedNBDevice simulator
"""
import unittest
from ZonedNBDevice import ZonedNBDevice


class TestZonedNBDevice(unittest.TestCase):
    
    def setUp(self):
        """Create a device with 5 zones of 64MB each"""
        self.zbd = ZonedNBDevice(nzones=5, zonesize=64)
    
    def test_write_rock_basic(self):
        """Test basic rock write operation"""
        data = bytearray(b"Hello, World!")
        wptr = self.zbd.write_rock(0, len(data), data)
        self.assertEqual(wptr, len(data))
    
    def test_read_rock_basic(self):
        """Test basic rock read operation"""
        data = bytearray(b"Test Data")
        self.zbd.write_rock(0, len(data), data)
        
        dest = bytearray(len(data))
        self.zbd.read_rock(0, len(data), dest)
        self.assertEqual(dest, data)
    
    def test_sequential_writes(self):
        """Test sequential writes advance write pointer correctly"""
        wptr = self.zbd.write_rock(0, 1024, bytearray(1024))
        self.assertEqual(wptr, 1024)
        
        wptr = self.zbd.write_rock(1024, 512, bytearray(512))
        self.assertEqual(wptr, 1536)
    
    def test_write_not_at_wptr_fails(self):
        """Test that writing not at write pointer raises exception"""
        with self.assertRaises(Exception) as ctx:
            self.zbd.write_rock(5000, 100, bytearray(100))
        self.assertIn("does not match write ptr", str(ctx.exception))
    
    def test_read_nonexistent_rock_fails(self):
        """Test that reading non-existent rock raises exception"""
        dest = bytearray(100)
        with self.assertRaises(Exception) as ctx:
            self.zbd.read_rock(99999, 100, dest)
        self.assertIn("No rock exists", str(ctx.exception))
    
    def test_zone_reset(self):
        """Test zone reset allows rewriting from start"""
        self.zbd.write_rock(0, 1024, bytearray(1024))
        self.zbd.reset_zone(zoneid=0)
        
        # Should be able to write from 0 again
        wptr = self.zbd.write_rock(0, 512, bytearray(512))
        self.assertEqual(wptr, 512)
    
    def test_insufficient_zone_space_fails(self):
        """Test that writing beyond zone capacity raises exception"""
        zone_size = 64 * 1024 * 1024  # 64MB
        with self.assertRaises(Exception) as ctx:
            self.zbd.write_rock(0, zone_size + 1, bytearray(zone_size + 1))
        self.assertIn("Not enough space", str(ctx.exception))
    
    def test_read_size_mismatch_fails(self):
        """Test that reading with wrong size raises exception"""
        data = bytearray(b"Test")
        self.zbd.write_rock(0, len(data), data)
        
        dest = bytearray(100)  # Wrong size
        with self.assertRaises(Exception) as ctx:
            self.zbd.read_rock(0, 100, dest)
        self.assertIn("Rock size incorrect", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
