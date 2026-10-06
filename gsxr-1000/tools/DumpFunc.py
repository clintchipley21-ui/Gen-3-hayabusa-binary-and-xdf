# Ghidra postscript (Jython): decompile a comma-separated list of function entry addresses
# (hex) and print their C, so we can read the control logic. arg0 = "addr1,addr2,...", arg1=outfile.
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

a = getScriptArgs()
addrs = [x for x in a[0].split(',') if x]
outfile = a[1] if len(a) > 1 else '/tmp/func.c'
fm = currentProgram.getFunctionManager()
af = currentProgram.getAddressFactory().getDefaultAddressSpace()
dif = DecompInterface()
dif.openProgram(currentProgram)
mon = ConsoleTaskMonitor()
fh = open(outfile, 'w')
for h in addrs:
    ea = af.getAddress(h)
    f = fm.getFunctionContaining(ea)
    if f is None:
        fh.write('// no function at %s\n' % h); continue
    res = dif.decompileFunction(f, 60, mon)
    fh.write('\n// ===== FUNCTION 0x%s (%s) =====\n' % (h, f.getName()))
    if res is not None and res.getDecompiledFunction() is not None:
        fh.write(res.getDecompiledFunction().getC())
    else:
        fh.write('// decompile failed\n')
fh.close()
print('[DumpFunc] wrote %s' % outfile)
