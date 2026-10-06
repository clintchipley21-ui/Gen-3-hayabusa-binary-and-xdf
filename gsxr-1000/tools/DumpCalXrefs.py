# Ghidra headless postscript (Jython): dump code->calibration references.
# Writes <outfile> with: from_addr  to_addr  refType  context
# outfile is passed as the first script arg.
import os
from ghidra.program.model.symbol import RefType

args = getScriptArgs()
outfile = args[0] if args and len(args) > 0 else '/tmp/calxrefs.tsv'

LO = 0x150000
HI = 0x1B0000

rm = currentProgram.getReferenceManager()
listing = currentProgram.getListing()
fm = currentProgram.getFunctionManager()
fh = open(outfile, 'w')
n = 0
it = rm.getReferenceIterator(currentProgram.getMinAddress())
while it.hasNext():
    r = it.next()
    to = r.getToAddress()
    if to is None:
        continue
    off = to.getOffset()
    if LO <= off < HI:
        frm = r.getFromAddress()
        rt = r.getReferenceType()
        cu = listing.getCodeUnitAt(frm)
        mn = cu.getMnemonicString() if cu is not None else '?'
        fn = fm.getFunctionContaining(frm)
        fe = ('%06x' % fn.getEntryPoint().getOffset()) if fn is not None else '-'
        fh.write('%06x\t%06x\t%s\t%s\t%s\n' % (frm.getOffset(), off, rt, mn, fe))
        n += 1
fh.close()
print('[DumpCalXrefs] wrote %d references to %s' % (n, outfile))

# also dump function count + instruction count for a sanity signal
fns = currentProgram.getFunctionManager().getFunctionCount()
ic = listing.getNumInstructions()
print('[DumpCalXrefs] functions=%d instructions=%d' % (fns, ic))
