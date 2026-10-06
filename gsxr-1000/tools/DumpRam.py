# Ghidra postscript (Jython): dump references to the sensor-RAM window 0xFEF02000-0xFEF03000
# (engine RPM, TPS, gear, wheel speed live here on the Hayabusa), with containing function.
# out: from_addr  to_ram  refType  mnem  func_entry
args = getScriptArgs()
outfile = args[0] if args else '/tmp/ramxrefs.tsv'
LO = 0xFEF02000
HI = 0xFEF03000
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
        cu = listing.getCodeUnitAt(frm)
        mn = cu.getMnemonicString() if cu is not None else '?'
        fn = fm.getFunctionContaining(frm)
        fe = ('%06x' % fn.getEntryPoint().getOffset()) if fn is not None else '-'
        fh.write('%06x\t%08x\t%s\t%s\t%s\n' % (frm.getOffset(), off, r.getReferenceType(), mn, fe))
        n += 1
fh.close()
print('[DumpRam] wrote %d sensor-RAM references to %s' % (n, outfile))
