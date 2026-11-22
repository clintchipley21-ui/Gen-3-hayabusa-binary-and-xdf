#!/usr/bin/env python3
"""capture_flash.py -- extract a Gen-3 Hayabusa diagnostic/flash exchange.

The seed/key (or RH850 ID-auth) that gates ECU writing is not recoverable
from the static image (see ../../re/boot/pbl-flash-protocol.md). The practical
unlock is to CAPTURE one real exchange from an OEM / MPVI / Tactrix flash
session and replay/derive from it. This tool does exactly that.

It reassembles ISO-TP (ISO 15765-2) on the Suzuki diagnostic IDs
(request 0x7B0 -> response 0x7B1 by default), decodes the KWP2000-on-CAN
services, and pulls out:
  * DiagnosticSessionControl (0x10) transitions
  * SecurityAccess (0x27) seed  -> key pairs           [the unlock]
  * ReadDataByIdentifier / ReadMemoryByAddress responses (ECU identity)
  * any RequestDownload/TransferData (0x34/0x36/0x37) or boot-loader frames

Inputs:
  * a Vector .asc log file (offline), OR
  * a live CAN bus via python-can (--live), e.g. a canable 2.0 / SocketCAN

Outputs:
  * a readable decode on stdout
  * --json <file>  : structured request/response pairs
  * --replay <file>: extracted seed/key (and ID-auth) pairs for seedkey.py

Usage:
  python3 capture_flash.py trace.asc --json out.json --replay keys.json
  python3 capture_flash.py --live --channel can0 --bitrate 500000 --json out.json

This tool only READS. It never transmits to the ECU.
"""
import argparse
import json
import re
import sys

REQ_ID = 0x7B0            # tester -> ECU (confirmed, Gen-3 Hayabusa)
RSP_ID = 0x7B1            # ECU -> tester

SID_NAME = {
    0x10: "DiagnosticSessionControl", 0x11: "ECUReset",
    0x22: "ReadDataByIdentifier", 0x23: "ReadMemoryByAddress",
    0x27: "SecurityAccess", 0x2E: "WriteDataByIdentifier",
    0x31: "RoutineControl", 0x34: "RequestDownload",
    0x36: "TransferData", 0x37: "RequestTransferExit",
    0x3E: "TesterPresent", 0x81: "StartCommunication",
    0x82: "StopCommunication", 0x85: "ControlDTCSetting",
}


# --------------------------------------------------------------------------
# ISO-TP (ISO 15765-2) reassembly: one direction = one Reassembler
# --------------------------------------------------------------------------
class IsoTp:
    def __init__(self):
        self.buf = bytearray()
        self.remaining = 0
        self.active = False

    def feed(self, data):
        """Feed one 8-byte CAN payload. Return a completed message or None."""
        if not data:
            return None
        pci = data[0] >> 4
        if pci == 0x0:                         # Single Frame
            n = data[0] & 0x0F
            return bytes(data[1:1 + n])
        if pci == 0x1:                         # First Frame
            length = ((data[0] & 0x0F) << 8) | data[1]
            self.buf = bytearray(data[2:8])
            self.remaining = length - len(self.buf)
            self.active = True
            return None
        if pci == 0x2:                         # Consecutive Frame
            if not self.active:
                return None
            take = min(7, self.remaining)
            self.buf.extend(data[1:1 + take])
            self.remaining -= take
            if self.remaining <= 0:
                self.active = False
                return bytes(self.buf)
            return None
        # 0x3 = Flow Control: transport-level, no payload to reassemble
        return None


# --------------------------------------------------------------------------
# Frame sources
# --------------------------------------------------------------------------
_ASC_RE = re.compile(
    r"^\s*[\d.]+\s+\d+\s+([0-9A-Fa-f]+)\s+(Rx|Tx)\s+d\s+(\d+)\s+((?:[0-9A-Fa-f]{2}\s+)*)",
)


def frames_from_asc(path):
    """Yield (can_id:int, data:bytes) from a Vector .asc log."""
    with open(path, "r", errors="replace") as f:
        for line in f:
            m = _ASC_RE.match(line)
            if not m:
                continue
            cid = int(m.group(1), 16)
            dlc = int(m.group(3))
            byts = bytes(int(b, 16) for b in m.group(4).split())[:dlc]
            yield cid, byts


def frames_from_live(channel, bustype, bitrate, seconds):
    try:
        import can
    except ImportError:
        sys.exit("error: python-can required for --live. pip install python-can")
    import time
    bus = can.interface.Bus(channel=channel, bustype=bustype, bitrate=bitrate)
    end = time.monotonic() + seconds
    try:
        while time.monotonic() < end:
            msg = bus.recv(timeout=0.5)
            if msg is not None and not msg.is_error_frame:
                yield msg.arbitration_id, bytes(msg.data)
    finally:
        bus.shutdown()


# --------------------------------------------------------------------------
# Decode
# --------------------------------------------------------------------------
def decode_session(frames, req_id, rsp_id, verbose=False):
    req_tp, rsp_tp = IsoTp(), IsoTp()
    events = []          # ordered (dir, bytes)
    for cid, data in frames:
        if cid == req_id:
            msg = req_tp.feed(data)
            if msg:
                events.append(("REQ", msg))
        elif cid == rsp_id:
            msg = rsp_tp.feed(data)
            if msg:
                events.append(("RSP", msg))

    pairs, seedkeys = [], []
    pending_seed = None
    for direction, msg in events:
        if not msg:
            continue
        sid = msg[0]
        neg = (sid == 0x7F)
        eff = msg[1] if neg and len(msg) > 1 else sid
        name = SID_NAME.get(eff & 0x3F if eff >= 0x40 else eff, "?")
        rec = {"dir": direction, "sid": eff & 0x7F, "service": name,
               "neg": neg, "bytes": msg.hex()}
        pairs.append(rec)

        # SecurityAccess seed/key extraction
        base = sid - 0x40 if sid >= 0x40 else sid
        if base == 0x27 and not neg and len(msg) >= 2:
            sub = msg[1]
            if direction == "RSP" and sub % 2 == 1:           # seed response (odd)
                pending_seed = {"level": sub, "seed": msg[2:].hex()}
            elif direction == "REQ" and sub % 2 == 0 and pending_seed:  # key request (even)
                seedkeys.append({"level": pending_seed["level"],
                                 "seed": pending_seed["seed"],
                                 "key": msg[2:].hex()})
                pending_seed = None
        if verbose:
            print(f"  {direction}  {name:<26} {msg.hex()}")
    return pairs, seedkeys


def main():
    ap = argparse.ArgumentParser(description="Extract a Hayabusa diagnostic/flash exchange.")
    ap.add_argument("trace", nargs="?", help="Vector .asc log (offline mode)")
    ap.add_argument("--live", action="store_true", help="capture from a live CAN bus")
    ap.add_argument("--channel", default="can0")
    ap.add_argument("--bustype", default="socketcan")
    ap.add_argument("--bitrate", type=int, default=500000)
    ap.add_argument("--seconds", type=float, default=60.0, help="live capture duration")
    ap.add_argument("--req-id", type=lambda x: int(x, 0), default=REQ_ID)
    ap.add_argument("--rsp-id", type=lambda x: int(x, 0), default=RSP_ID)
    ap.add_argument("--json", help="write structured request/response pairs")
    ap.add_argument("--replay", help="write extracted seed/key pairs for seedkey.py")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if args.live:
        frames = frames_from_live(args.channel, args.bustype, args.bitrate, args.seconds)
    elif args.trace:
        frames = frames_from_asc(args.trace)
    else:
        ap.error("give a .asc trace file or --live")

    pairs, seedkeys = decode_session(frames, args.req_id, args.rsp_id, args.verbose)

    print(f"diagnostic messages reassembled: {len(pairs)} "
          f"(req 0x{args.req_id:03X} / rsp 0x{args.rsp_id:03X})")
    svc = {}
    for p in pairs:
        svc[p["service"]] = svc.get(p["service"], 0) + 1
    for name, n in sorted(svc.items(), key=lambda x: -x[1]):
        print(f"  {n:5d}  {name}")
    if seedkeys:
        print(f"\n*** {len(seedkeys)} SecurityAccess seed/key pair(s) captured ***")
        for sk in seedkeys:
            print(f"  level 0x{sk['level']:02X}  seed={sk['seed']}  key={sk['key']}")
    else:
        print("\nNo SecurityAccess seed/key exchange found in this capture.")
        print("(Both on-disk .asc traces are passive sniffs; capture a real "
              "OEM/MPVI flash session with --live to get the exchange.)")

    if args.json:
        with open(args.json, "w") as f:
            json.dump(pairs, f, indent=2)
        print(f"wrote {args.json}")
    if args.replay:
        with open(args.replay, "w") as f:
            json.dump({"req_id": args.req_id, "rsp_id": args.rsp_id,
                       "seedkeys": seedkeys}, f, indent=2)
        print(f"wrote {args.replay}")


if __name__ == "__main__":
    main()
