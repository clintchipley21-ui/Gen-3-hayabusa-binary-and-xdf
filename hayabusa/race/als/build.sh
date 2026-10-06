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

# --- rolling anti-lag at 0xBE000 (external refs resolved to their stock addresses)
$AS -o "$OUT/als.o" "$HERE/als.s"
$LD -e 0 -Ttext=0xbe000 --defsym FUN_5BDB4=0x5bdb4 --defsym FUN_2C396=0x2c396 \
    -o "$OUT/als.elf" "$OUT/als.o"
$OC -O binary --only-section=.als_code "$OUT/als.elf" "$OUT/als.bin"

# --- auto-upshift at 0xBE148 (runs after the stock PAIR output mapper FUN_5DB5E)
$AS -o "$OUT/autoshift.o" "$HERE/autoshift.s"
$LD -e 0 -Ttext=0xbe148 --defsym FUN_5DB5E=0x5db5e -o "$OUT/autoshift.elf" "$OUT/autoshift.o"
$OC -O binary --only-section=.as_code "$OUT/autoshift.elf" "$OUT/autoshift.bin"

# --- hook words (replace one jarl each): 0x5BE02->ALS_TICK, 0x5DC9E->AUTOSHIFT_TICK
hook() { # addr target
  printf '\t.section .h,"ax"\n\tjarl %s, lp\n' "$2" > "$OUT/h.s"
  $AS -o "$OUT/h.o" "$OUT/h.s"
  $LD -e 0 -Ttext=$1 --defsym ALS_TICK=0xbe000 --defsym AUTOSHIFT_TICK=0xbe148 \
      -o "$OUT/h.elf" "$OUT/h.o"
  $OC -O binary --only-section=.h "$OUT/h.elf" "$OUT/h.bin"
  printf '%s %s = ' "$1" "$2"; od -An -tx1 "$OUT/h.bin" | tr -d ' \n'; echo
}
echo "als.bin       $(wc -c < "$OUT/als.bin") bytes @0xBE000"
echo "autoshift.bin $(wc -c < "$OUT/autoshift.bin") bytes @0xBE148"
echo "hooks:"
hook 0x5dc9e AUTOSHIFT_TICK
