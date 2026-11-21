# Ghidra headless post-script: decompile the 5JCUSJ40 full dump and export C.
#
# This reproduces the repo's hayabusa/re/ artifacts for the 5JCU/5JE0 firmware
# line (the uploads), which could NOT be decompiled before because the only
# prior copy (5JCUSJ40.ori) had its whole code half encrypted. The decrypted
# full dump (5JCUSJ40-full.bin) is plaintext RH850/F1L code.
#
# Run (needs Ghidra >= 11, which bundles the RH850 processor module):
#
#   analyzeHeadless <proj_dir> busa5jcu \
#       -import hayabusa/stock/other/5JCUSJ40-full.bin \
#       -loader BinaryLoader -loader-baseAddr 0x0 \
#       -processor "RH850:LE:32:default" \
#       -postScript ghidra_export_fulldump.py <out_dir> \
#       -deleteProject
#
# The device is RH850/F1L (boot block device-ID table: R7F701201/202/204/205/206,
# R7F701Z04-Z07). Flash is mapped at 0x0; on-chip RAM/peripherals live at
# 0xFE000000-0xFFFFFFFF (match the existing decompile's ram:fffxxxxx addresses).
#
# @category Suzuki
import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

args = getScriptArgs()
out_dir = args[0] if args else os.getcwd()
prog = currentProgram
fm = prog.getFunctionManager()
mon = ConsoleTaskMonitor()

ifc = DecompInterface()
ifc.openProgram(prog)

c_path = os.path.join(out_dir, "all_functions_5jcu.c")
idx_path = os.path.join(out_dir, "functions_5jcu.csv")
nfun = 0
with open(c_path, "w") as cf, open(idx_path, "w") as xf:
    xf.write("address,name,size_bytes\n")
    for fn in fm.getFunctions(True):
        ep = fn.getEntryPoint()
        addr = int(ep.getOffset())
        body = fn.getBody()
        size = int(body.getNumAddresses())
        xf.write("0x%08x,%s,%d\n" % (addr, fn.getName(), size))
        cf.write("// ===== %s @ 0x%08x (%d bytes) =====\n" % (fn.getName(), addr, size))
        res = ifc.decompileFunction(fn, 60, mon)
        if res and res.decompileCompleted():
            cf.write(res.getDecompiledFunction().getC())
        else:
            cf.write("// <decompilation failed>\n")
        cf.write("\n\n")
        nfun += 1

print("exported %d functions to %s" % (nfun, c_path))
