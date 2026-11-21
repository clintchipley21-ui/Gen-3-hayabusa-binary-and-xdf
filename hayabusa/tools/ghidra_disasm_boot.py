# Ghidra postscript: force-disassemble the reset/boot code from 0x0 and 0x10000, follow it,
# run SymbolicPropogator, and report the value written to gp (r4). Prints boot disasm.
from ghidra.app.cmd.disassemble import DisassembleCommand
from ghidra.program.util import SymbolicPropogator
from ghidra.program.model.lang import Register
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.model.address import AddressSet

a = getScriptArgs()
outfile = a[0] if a else '/tmp/boot.txt'
fh = open(outfile, 'w')
af = currentProgram.getAddressFactory().getDefaultAddressSpace()
mon = ConsoleTaskMonitor()
listing = currentProgram.getListing()
gp = currentProgram.getRegister("gp") or currentProgram.getRegister("r4")

# reset vector: first 4 bytes at 0x0 often a jr/jmp; just disassemble from 0x0 and 0x10000
mem = currentProgram.getMemory()
b0 = mem.getInt(af.getAddress(0)) & 0xFFFFFFFF
fh.write("word@0x0 = 0x%08x\n" % b0)
for start in (0x0, 0x10000, b0 & 0x1FFFFF):
    try:
        cmd = DisassembleCommand(af.getAddress(start), None, True)
        cmd.applyTo(currentProgram, mon)
    except Exception as e:
        fh.write("disasm %x failed: %s\n" % (start, e))

# print boot disasm from 0x0
for start in (0x0, 0x10000):
    fh.write("\n== disasm from 0x%x ==\n" % start)
    ins = listing.getInstructionAt(af.getAddress(start))
    k = 0
    while ins is not None and k < 60:
        fh.write("0x%08x  %s\n" % (ins.getAddress().getOffset(), ins.toString()))
        ins = ins.getNext(); k += 1

# SymbolicPropogator from 0x0 and 0x10000 to catch gp set
def propagate(start):
    sp = SymbolicPropogator(currentProgram)
    try:
        from ghidra.program.util import ContextEvaluatorAdapter
        sp.flowConstants(af.getAddress(start), None, None, True, mon)
    except Exception as e:
        fh.write("prop %x err %s\n" % (start, e))
        return
    # sample gp value at a range of addresses
    for probe in (0x10100, 0x14000, 0x064506, 0x02c8fe):
        try:
            v = sp.getRegisterValue(af.getAddress(probe), gp)
            if v is not None and not v.isRegisterRelativeValue():
                fh.write("gp @0x%x = 0x%08x\n" % (probe, v.getValue() & 0xFFFFFFFF))
        except Exception:
            pass

propagate(0x0)
propagate(0x10000)

# scan boot code (0x0-0x400, 0x10000-0x10400) for instructions writing gp
fh.write("\n== gp writes in boot ==\n")
for lo, hi in ((0, 0x600), (0x10000, 0x10600)):
    ins = listing.getInstructionAt(af.getAddress(lo))
    while ins is not None and ins.getAddress().getOffset() < hi:
        outs = ins.getResultObjects()
        if outs and any(isinstance(o, Register) and o.getName() == gp.getName() for o in outs):
            fh.write("0x%08x  %s\n" % (ins.getAddress().getOffset(), ins.toString()))
        ins = ins.getNext()
fh.close()
print('[DisasmBoot] wrote %s' % outfile)
