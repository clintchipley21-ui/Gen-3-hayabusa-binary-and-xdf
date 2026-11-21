#!/usr/bin/env python3
"""Decode a Motorola S-record (.mot/.s19/.srec) flash dump into a flat binary.

Used for the Gen-3 Hayabusa 5JCUSJ40 full-flash read produced by Renesas Flash
Programmer (RFP3). The S3 records cover the entire 0x000000-0x1FFFFF RH850/F1L
address space; gaps are filled with 0xFF (erased flash).

    python3 decode_srec.py INPUT.mot OUTPUT.bin [--size 0x200000]

Reproduces hayabusa/stock/other/5JCUSJ40-full.bin
(sha256 ac23ced9887ac9c184b2deb3cabd0c96853a7fcc2a5da14560f4c8a3d8457dd0).
"""
import sys, hashlib, argparse

def decode(path, size):
    img = bytearray(b"\xff" * size)
    covered = 0
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if len(ln) < 4 or ln[0] != "S":
                continue
            t = ln[1]
            if t not in "123":
                continue  # S0 header, S5/6 counts, S7/8/9 start-addr: no data payload we keep
            alen = {"1": 4, "2": 6, "3": 8}[t]
            count = int(ln[2:4], 16)
            addr = int(ln[4:4 + alen], 16)
            payload = ln[4 + alen: 4 + count * 2 - 2]  # drop 1-byte checksum
            data = bytes.fromhex(payload)
            for i, b in enumerate(data):
                a = addr + i
                if 0 <= a < size:
                    img[a] = b
                    covered += 1
    return img, covered

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input"); ap.add_argument("output")
    ap.add_argument("--size", default="0x200000")
    a = ap.parse_args()
    size = int(a.size, 0)
    img, covered = decode(a.input, size)
    with open(a.output, "wb") as f:
        f.write(img)
    print("wrote %s  size=0x%X  covered=%d bytes  sha256=%s"
          % (a.output, size, covered, hashlib.sha256(img).hexdigest()))

if __name__ == "__main__":
    main()
