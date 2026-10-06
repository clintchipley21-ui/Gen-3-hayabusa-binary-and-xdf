# Ghidra postscript (Jython): for every CALL in the program, resolve its arguments to either
# a constant (C:val) or a RAM/ROM address (M:addr), via the decompiler high-p-code. This lets us
# find the table-lookup routine(s) (called with a descriptor-range constant) and, per call, the
# X/Y input RAM variables of each map - the GSX-R's own map_links, from its code.
#
# out columns: caller_entry  callsite  target  argidx  resolved
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

args = getScriptArgs()
outfile = args[0] if args else '/tmp/lookups.tsv'

fm = currentProgram.getFunctionManager()
dif = DecompInterface()
dif.openProgram(currentProgram)
mon = ConsoleTaskMonitor()

def resolve(vn, depth=0):
    """Resolve a varnode to ('C',const) or ('M',addr) or None, chasing defs a few levels."""
    if vn is None or depth > 6:
        return None
    if vn.isConstant():
        return ('C', vn.getOffset() & 0xFFFFFFFF)
    if vn.isAddress() or vn.isUnique() is False and vn.getAddress() is not None and vn.getAddress().isMemoryAddress():
        a = vn.getAddress()
        if a is not None and a.isMemoryAddress():
            return ('M', a.getOffset() & 0xFFFFFFFF)
    d = vn.getDef()
    if d is None:
        a = vn.getAddress()
        if a is not None and a.isMemoryAddress():
            return ('M', a.getOffset() & 0xFFFFFFFF)
        return None
    op = d.getMnemonic()
    ins = d.getInputs()
    if op == 'LOAD' and len(ins) >= 2:
        r = resolve(ins[1], depth + 1)
        if r and r[0] == 'C':
            return ('M', r[1])          # load from constant address = that RAM/ROM var
        return r
    if op in ('COPY', 'CAST', 'INT_ZEXT', 'INT_SEXT', 'INT_2COMP', 'SUBPIECE'):
        return resolve(ins[0], depth + 1)
    if op in ('INT_ADD', 'PTRADD', 'PTRSUB') and len(ins) >= 2:
        a = resolve(ins[0], depth + 1)
        b = resolve(ins[1], depth + 1)
        if a and b and a[0] == 'C' and b[0] == 'C':
            return ('C', (a[1] + b[1]) & 0xFFFFFFFF)
        # base + const offset: prefer the memory/base operand
        if a and a[0] == 'M':
            return a
        if b and b[0] == 'M':
            return b
        return a or b
    return None

fh = open(outfile, 'w')
n = 0
cnt = 0
it = fm.getFunctions(True)
while it.hasNext():
    f = it.next()
    cnt += 1
    try:
        res = dif.decompileFunction(f, 45, mon)
        hf = res.getHighFunction() if res is not None else None
        if hf is None:
            continue
        ent = f.getEntryPoint().getOffset()
        ops = hf.getPcodeOps()
        while ops.hasNext():
            op = ops.next()
            mn = op.getMnemonic()
            if mn not in ('CALL', 'CALLIND'):
                continue
            site = op.getSeqnum().getTarget().getOffset()
            ins = op.getInputs()
            tgt = ins[0]
            tgts = ('%x' % tgt.getAddress().getOffset()) if tgt.isAddress() else 'IND'
            # arguments are ins[1:]
            for i in range(1, len(ins)):
                r = resolve(ins[i])
                if r is None:
                    continue
                fh.write('%x\t%x\t%s\t%d\t%s:%x\n' % (ent, site, tgts, i - 1, r[0], r[1]))
                n += 1
    except Exception:
        pass
fh.close()
print('[DumpLookups] decompiled %d functions, wrote %d resolved call-args to %s' % (cnt, n, outfile))
