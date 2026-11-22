#!/usr/bin/env python3
"""seedkey.py -- pluggable auth providers for the Gen-3 Hayabusa flasher.

The write gate is unsolved statically (see ../../re/boot/pbl-flash-protocol.md).
This module keeps auth behind one interface so that, as soon as a capture or a
bench test reveals the mechanism, it drops in without touching the flash logic.

Providers implement:  key_for(seed: bytes, level: int) -> bytes
and/or:                id_code() -> bytes            (RH850 ID-authentication)

Three strategies, matching the two documented unlock paths:
  * ReplayProvider  -- exact-match replay of a captured seed->key pair
                       (from capture_flash.py --replay). Works when the ECU
                       re-uses a fixed seed, or for a one-shot bench replay.
  * IdCodeProvider  -- the RH850 16-byte ID-authentication value, read straight
                       from the flash image (prime candidate: the 0x10 option
                       area). Test this first on a bench ECU.
  * DerivedProvider -- where a reversed/derived seed->key algorithm goes once
                       one is known. Raises until implemented, on purpose.
"""
from __future__ import annotations
import json


class AuthProvider:
    def key_for(self, seed: bytes, level: int) -> bytes:
        raise NotImplementedError
    def id_code(self) -> bytes:
        raise NotImplementedError("this provider has no ID-code")


class ReplayProvider(AuthProvider):
    """Replay seed->key pairs captured from a real flash session."""
    def __init__(self, replay_path: str):
        with open(replay_path) as f:
            data = json.load(f)
        self._map = {}            # (level, seed_hex) -> key bytes
        for sk in data.get("seedkeys", []):
            self._map[(sk["level"], sk["seed"].lower())] = bytes.fromhex(sk["key"])
        if not self._map:
            raise ValueError(f"{replay_path} has no seed/key pairs")

    def key_for(self, seed: bytes, level: int) -> bytes:
        k = self._map.get((level, seed.hex()))
        if k is None:
            raise KeyError(
                f"no captured key for level 0x{level:02X} seed {seed.hex()}; "
                "the ECU issued a seed not in the replay set (non-fixed seed -> "
                "the algorithm must be derived, not replayed)")
        return k


class IdCodeProvider(AuthProvider):
    """RH850 ID-authentication: a 16-byte code read from the flash image.

    Candidate offset is the option/ID area at 0x10 (the A55A5AA5 pattern).
    Confirm on a bench ECU before trusting it.
    """
    OPTION_ID_OFFSET = 0x10
    ID_LEN = 16

    def __init__(self, image: bytes, offset: int | None = None):
        off = self.OPTION_ID_OFFSET if offset is None else offset
        self._id = bytes(image[off:off + self.ID_LEN])
        if len(self._id) != self.ID_LEN:
            raise ValueError("image too small for an ID code at that offset")

    def id_code(self) -> bytes:
        return self._id

    @classmethod
    def from_file(cls, path: str, offset: int | None = None) -> "IdCodeProvider":
        with open(path, "rb") as f:
            return cls(f.read(), offset)


class DerivedProvider(AuthProvider):
    """Reversed seed->key algorithm. Fill in once a capture reveals it."""
    def key_for(self, seed: bytes, level: int) -> bytes:
        raise NotImplementedError(
            "seed->key algorithm not yet derived -- capture >=1 exchange with "
            "capture_flash.py, then implement the transform here (and add a "
            "self-test against the captured pair).")


if __name__ == "__main__":
    import argparse, sys
    ap = argparse.ArgumentParser(description="Inspect/test an auth provider.")
    ap.add_argument("--image", help="flash .bin to read the RH850 ID code from")
    ap.add_argument("--offset", type=lambda x: int(x, 0), default=None)
    ap.add_argument("--replay", help="captured seed/key json to load")
    args = ap.parse_args()
    if args.image:
        p = IdCodeProvider.from_file(args.image, args.offset)
        print("RH850 ID-code candidate:", p.id_code().hex())
    if args.replay:
        p = ReplayProvider(args.replay)
        print(f"loaded {len(p._map)} captured seed/key pair(s)")
    if not (args.image or args.replay):
        ap.print_help(); sys.exit(1)
