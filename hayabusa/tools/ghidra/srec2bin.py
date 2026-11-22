import sys

def parse(path):
    lo, hi = None, None
    chunks = []  # (addr, bytes)
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line[0] != 'S':
                continue
            t = line[1]
            if t not in '123':
                continue
            count = int(line[2:4], 16)
            alen = {'1': 4, '2': 6, '3': 8}[t]
            addr = int(line[4:4+alen], 16)
            data = bytes.fromhex(line[4+alen:4+alen+2*(count-(alen//2)-1)])
            chunks.append((addr, data))
            if lo is None or addr < lo:
                lo = addr
            end = addr + len(data)
            if hi is None or end > hi:
                hi = end
    size = hi - lo
    buf = bytearray(b'\xff' * size)
    covered = bytearray(size)
    for addr, data in chunks:
        off = addr - lo
        buf[off:off+len(data)] = data
        for i in range(len(data)):
            covered[off+i] = 1
    # find gaps
    gaps = []
    in_gap = False
    gstart = 0
    for i in range(size):
        if not covered[i] and not in_gap:
            in_gap = True; gstart = i
        elif covered[i] and in_gap:
            in_gap = False; gaps.append((lo+gstart, lo+i))
    if in_gap:
        gaps.append((lo+gstart, lo+size))
    return lo, hi, buf, gaps

if __name__ == '__main__':
    lo, hi, buf, gaps = parse(sys.argv[1])
    print(f"range: 0x{lo:08X} .. 0x{hi:08X}  size=0x{hi-lo:X} ({hi-lo} bytes)")
    print(f"gaps: {len(gaps)}")
    for g in gaps[:20]:
        print(f"  gap 0x{g[0]:08X}..0x{g[1]:08X} (0x{g[1]-g[0]:X})")
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'wb') as f:
            f.write(buf)
        print("wrote", sys.argv[2], len(buf), "bytes")
