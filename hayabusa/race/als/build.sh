#!/bin/sh
# Assemble the custom code blobs and print their bytes + install hooks.
#   als.s       -> 0xBE000 rolling anti-lag (must reproduce the SD-v4.1 bytes exactly)
#   autoshift.s -> 0xBE148 auto-upshift / air-shifter (PAIR-output pulse)
#
# Needs a GNU binutils built for RH850 (v850e3v5): as-new, ld-new, objcopy, objdump.
# Point TOOLS at that build dir (default: the paths used during development).
#
#   TOOLS=/path/to/binutils-build sh build.sh
#
# Output: als.bin, autoshift.bin and the 4-byte hook words, under ./out/.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
TOOLS=${TOOLS:-/tmp/claude-0/-home-user-Gen-3-hayabusa-binary-and-xdf/875e2d62-f3f0-514d-8c44-299ce590e8e4/scratchpad/bu-build}
AS="$TOOLS/gas/as-new -mv850e3v5"
LD="$TOOLS/ld/ld-new"
OC="$TOOLS/binutils/objcopy"
OUT="$HERE/out"; mkdir -p "$OUT"

# --- rolling anti-lag at 0xBE000 (SET-hold trigger). ALS_LIMIT/ALS_IS_ACTIVE are pinned (.org) to
#     their original offsets so the stock hooks still land; only ALS_TICK changed. apply_patches.py
#     installs this als.bin at 0xBE000 (falling back to the SD-v4.1 START-trigger bytes if it is absent).
$AS -o "$OUT/als.o" "$HERE/als.s"
$LD -e 0 -Ttext=0xbe000 --defsym FUN_5BDB4=0x5bdb4 --defsym FUN_2C396=0x2c396 \
    -o "$OUT/als.elf" "$OUT/als.o"
$OC -O binary --only-section=.als_code "$OUT/als.elf" "$OUT/als.bin"

# --- auto-upshift at 0xBE148 (runs after the stock PAIR output mapper FUN_5DB5E)
$AS -o "$OUT/autoshift.o" "$HERE/autoshift.s"
$LD -e 0 -Ttext=0xbe148 --defsym FUN_5DB5E=0x5db5e -o "$OUT/autoshift.elf" "$OUT/autoshift.o"
$OC -O binary --only-section=.as_code "$OUT/autoshift.elf" "$OUT/autoshift.bin"

# --- boost control at 0xBE280 (runs after the stock routine at the 0x5dca2 call site, FUN_5DC64)
$AS -o "$OUT/boost.o" "$HERE/boost.s"
$LD -e 0 -Ttext=0xbe280 --defsym FUN_5DC64=0x5dc64 -o "$OUT/boost.elf" "$OUT/boost.o"
$OC -O binary --only-section=.boost_code "$OUT/boost.elf" "$OUT/boost.bin"

# --- hook words (replace one jarl each): 0x5BE02->ALS_TICK, 0x5DC9E->AUTOSHIFT_TICK, 0x5DCA2->BOOST_TICK
hook() { # addr target  (-> stdout: "addr target = <4 hex bytes>")
  printf '\t.section .h,"ax"\n\tjarl %s, lp\n' "$2" > "$OUT/h.s"
  $AS -o "$OUT/h.o" "$OUT/h.s"
  $LD -e 0 -Ttext=$1 --defsym ALS_TICK=0xbe000 --defsym AUTOSHIFT_TICK=0xbe148 \
      --defsym BOOST_TICK=0xbe280 -o "$OUT/h.elf" "$OUT/h.o"
  $OC -O binary --only-section=.h "$OUT/h.elf" "$OUT/h.bin"
  printf '%s %s = ' "$1" "$2"; od -An -tx1 "$OUT/h.bin" | tr -d ' \n'; echo
}
echo "als.bin       $(wc -c < "$OUT/als.bin") bytes @0xBE000"
echo "autoshift.bin $(wc -c < "$OUT/autoshift.bin") bytes @0xBE148"
echo "boost.bin     $(wc -c < "$OUT/boost.bin") bytes @0xBE280"
echo "hooks:"
hook 0x5dc9e AUTOSHIFT_TICK
# boost hook: write the 4-byte word next to the blob so apply_patches.py installs it (boost.hook)
hook 0x5dca2 BOOST_TICK | tee /dev/stderr | awk '{print $NF}' > "$OUT/boost.hook"
