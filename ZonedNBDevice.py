"""
This is an implementation of Rock support on a Zoned Null Block device

Interface is provided for reading and writing rocks to pages backed by-
a Zoned Null Block Device

read_rock(start_addr)

write_rock(start_addr, nbytes)
"""
__author__ = "Srikanth Mantravadi"
__email__ = "sxm6373@psu.edu"

from sortedcontainers import SortedDict
from LinkedList import LinkedList
import logging as lg

lg.basicConfig(level=lg.DEBUG)

# convert to hex
stohex = lambda s: hex(int(s, base=16))

# Constants
KB = 1024
PAGE_SIZE = 4 * KB


class NullBlkPage:
    size = PAGE_SIZE
    pagedata = None
    rocklist = None
    pageid: int
    staddr: int
    endaddr: int
    allocated: bool

    def __init__(self, st, end):
        self.pagedata = bytearray(self.size)
        self.rocklist = LinkedList()
        self.staddr = st
        self.pageid = int(st/(4*KB))
        self.endaddr = end
        # finally mark allocated
        self.mark_alloc()

    def mark_alloc(self):
        self.allocated = True
    def mark_dealloc(self):
        self.allocated = False

    def is_allocated(self):
        return self.allocated

    def clear_rocklist(self):
        if self.is_allocated():
            raise Exception("Cannot clear page, deallocate first")
        self.rocklist.clear()

class Zone:
    st_addr: int
    end_addr: int
    wptr: int
    id: int = None
    open: bool = False
    data = SortedDict()

    def __init__(self, id, st_addr, size):
        self.id = id
        self.size = size
        self.st_addr = st_addr

        self.end_addr = st_addr + size - 1
        self.reset()

    def reset(self):
        self.wptr = self.st_addr
        # for each page in zone, set pages to deallocated and clear its rocklist
        for k in self.data.keys():
            cpage = self.data.get(k)
            cpage.mark_dealloc()
            cpage.clear_rocklist()


class ZonedNBDevice:
    """
    Zoned Null Block Device
    """
    zones = []
    # assuming same size for all zones, value in MB
    zonesize: int

    def __init__(self, nzones, zonesize):
        """
        :param nzones: number of zones
        :param zonesize: size of zone in MB
        """
        self.zones = []
        zsize_mb = zonesize * 1024 * 1024
        self.zonesize = zsize_mb
        staddr = 0
        for i in range(nzones):
            zone_obj = Zone(i, staddr, zsize_mb)
            self.zones.append(zone_obj)
            staddr += zsize_mb

        ## Logging out for testing
        lg.debug("Num zones: %d, zone size: %dMB", nzones, zonesize)
        for j in range(nzones):
            curr_zone = self.zones[j]
            lg.debug("Zone#: %d, start addr: %s", curr_zone.id, hex(curr_zone.st_addr))

    def get_zone(self, addr):
        zoneid = int(addr / self.zonesize)
        return self.zones[zoneid]

    def lookup_page(self, addr, allocate=True):
        """
        Lookup the null blk page AND/OR allocate and return if none present
        :param addr: address in a given NB page
        :param allocate: (Default True), if set and no page exists, a page is allocated and returned
        :return:
        """
        zoneid = int(addr / self.zonesize)
        pageid = int(addr / PAGE_SIZE)

        zonedata = self.zones[zoneid].data
        pagedata: NullBlkPage = zonedata.get(pageid, None)

        is_page_dealloc = False
        if pagedata and not pagedata.is_allocated():
            is_page_dealloc = True
            pagedata = None

        if not allocate:
            return pagedata

        if not pagedata:
            # each page is a 4KB mutable array of bytes
            # allocate the mem for page now or if already present change status to alloc

            if is_page_dealloc:
                pagedata: NullBlkPage = zonedata.get(pageid)
                pagedata.mark_alloc()
                return pagedata

            zonedata.setdefault(pageid, NullBlkPage(pageid * 4 * KB, pageid * 4 * KB + PAGE_SIZE - 1))
            pagedata = zonedata.get(pageid)

        return pagedata

    def _zwrite(self, addr, nbytes, src) -> int:
        bytes_written = 0
        caddr = addr

        zoneid = int(caddr / self.zonesize)
        czone = self.zones[zoneid]

        # abandon if addr does not match write ptr
        if self.zones[zoneid].wptr != caddr:
            lg.error("Write address provided is not at write ptr")
            raise Exception("Address does not match write ptr")

        # abandon if not enough space in curr zone
        if czone.end_addr - czone.wptr + 1 < nbytes:
            lg.error("Not enough space in zone with id: %d", zoneid)
            raise Exception("Not enough space in zone")

        # allocate if needed and write data to required num of device pages
        src_idx = 0
        while bytes_written != nbytes:
            bytes_left = nbytes - bytes_written
            lg.debug("Written: %d, Left: %d", bytes_written, bytes_left)
            page: NullBlkPage = self.lookup_page(caddr)

            n = page.endaddr - caddr + 1 # current page capacity
            n = n if n < bytes_left else bytes_left
            byteaddr = caddr % PAGE_SIZE

            lg.debug("Writing %d bytes from %d to %d in zone %d. pageid: %d",
                     n, (byteaddr), (byteaddr+n-1), zoneid, page.pageid)

            for i in range(byteaddr, byteaddr + n):
                page.pagedata[i] = (src[src_idx])
                bytes_written += 1
                caddr += 1
                src_idx += 1

        # update and return wptr
        new_wptr = addr + nbytes
        self.zones[zoneid].wptr = new_wptr
        return new_wptr

    def _zread(self, addr, nbytes, dest):
        bytes_read = 0
        caddr = addr

        zoneid = int(caddr/self.zonesize)
        czone = self.zones[zoneid]

        # abandon if entire payload not in one zone
        if czone.end_addr - caddr + 1 < nbytes:
            lg.error("Data to be read must be part of one zone!")
            raise Exception("Data requested spans multiple zones")

        # abandon if dest buffer size not same as nbytes
        if len(dest) != nbytes:
            raise Exception("dest buffer size not same as payload size")

        destp = 0
        while bytes_read != nbytes:
            bytes_left = nbytes - bytes_read
            lg.debug("Read: %d, left %d", bytes_read, bytes_left)
            page: NullBlkPage = self.lookup_page(caddr)

            n = page.endaddr - caddr + 1
            n = n if n < bytes_left else bytes_left
            byteaddr = caddr % PAGE_SIZE

            lg.debug("Reading %d bytes from %d to %d in zone %d. pageid: %d",
                     n, byteaddr, (byteaddr+n-1), zoneid, page.pageid)

            for i in range(byteaddr, byteaddr+n):
                dest[destp] = page.pagedata[i]
                bytes_read += 1
                destp += 1
                caddr += 1

    def reset_zone(self, staddr=-1, zoneid=-1):
        zone = None
        if staddr > -1:
            zone = self.get_zone(staddr)

        if zoneid > -1:
            zone = self.zones[zoneid]

        if zone:
            lg.debug("Resetting zone with id: %d", zone.id)
            zone.reset()
            return

        raise Exception("Atleast one of staddr or zoneid is needed")

    def write_rock(self, saddr: int, nbytes: int, src: bytearray) -> int:
        """
        Write a rock from given start address using data in source buffer
        Note: This method can raise exceptions
        :param saddr: start address of rock
        :param nbytes: num of bytes to write
        :param src: source data buffer to write from
        :return: updated write ptr
        """
        stpage: NullBlkPage = self.lookup_page(saddr)

        new_wptr = self._zwrite(saddr, nbytes, src)
        # if write is successful, make an entry of rock
        stpage.rocklist.add({"key": saddr, "size": nbytes})

        return new_wptr

    def read_rock(self, saddr: int, nbytes: int, dest: bytearray):
        """
        Read a rock from the given starting address
        Note: This method can raise exceptions
        :param saddr: rock start address
        :param nbytes: num of bytes to read
        :param dest: destination buffer to copy rock data into
        """
        stpage: NullBlkPage = self.lookup_page(saddr, allocate=False)

        if not stpage:
            raise Exception("No rock exists at given address !")

        rock_data = stpage.rocklist.find(saddr)
        if not rock_data:
            raise Exception("No rock exists at given address !")

        rock_size = rock_data.data.get('size')
        if rock_size != nbytes:
            raise Exception("Rock size incorrect, unable to read arbitrary bytes in rock")

        self._zread(saddr, rock_size, dest)


"""
Driver logic:
"""
if __name__ == "__main__":
    zbd = ZonedNBDevice(5, 64)
    # write testing
    lg.debug("Write ptr at %d", zbd.write_rock(0, 1024, bytearray(1024)))
    lg.debug("Write ptr at %d", zbd.write_rock(1024, 6, bytearray(b"ABCDEF")))
    lg.debug("Write ptr at %d", zbd.write_rock(1030, 6, bytearray(b"123456")))
    wb = 9*KB
    lg.debug("Write ptr at %d", zbd.write_rock(1036, wb, bytearray(wb)))

    # read testing
    data = bytearray(1024)
    zbd.read_rock(0, 1024, data)
    lg.debug(str(data))

    # uncomment to reset zone and try the same write again
    # zbd.reset_zone(-1, 0)

    # write same data again, fails if zone is not reset
    # lg.debug("Write ptr at %d", zbd.write_rock(0, 1024, bytearray(1024)))
    # lg.debug("Write ptr at %d", zbd.write_rock(1024, 6, bytearray(b"ABCDEF")))
    # lg.debug("Write ptr at %d", zbd.write_rock(1030, 6, bytearray(b"123456")))
    # wb = 9 * KB
    # lg.debug("Write ptr at %d", zbd.write_rock(1036, wb, bytearray(wb)))