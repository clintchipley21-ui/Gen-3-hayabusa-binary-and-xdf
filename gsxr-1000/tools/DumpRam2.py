# Ghidra postscript (Jython): dump references to a RAM window [LO,HI) with containing function.
# args: outfile LO_hex HI_hex   (e.g. out.tsv FEBF6000 FEBF6500)
# out: from_addr  to_ram  refType  mnem  func_entry
args = getScriptArgs()
outfile = args[0] if args else '/tmp/ramxrefs.tsv'
LO = int(args[1], 16) if len(args) > 1 else 0xFEBF6000
HI = int(args[2], 16) if len(args) > 2 else 0xFEBF6500
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
print('[DumpRam2] wrote %d refs in [%08x,%08x) to %s' % (n, LO, HI, outfile))
