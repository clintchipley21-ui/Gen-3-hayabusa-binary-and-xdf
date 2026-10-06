# Ghidra postscript (Jython): find the V850 global pointer (gp/r4) value, set it as program
# context so gp-relative accesses resolve to absolute RAM addresses, then re-resolve every CALL
# argument (deeper chasing). Also report what gp-0x5bd2 resolves to (rev-cut engage signal).
#
# out: lookups2.tsv  (caller, site, target, argidx, resolved C:/M:)   + prints gp + a few probes
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.model.lang import Register
from ghidra.program.model.address import AddressSet

args = getScriptArgs()
outfile = args[0] if args else '/tmp/lookups2.tsv'
fm = currentProgram.getFunctionManager()
listing = currentProgram.getListing()
ctx = currentProgram.getProgramContext()
gp = currentProgram.getRegister("gp") or currentProgram.getRegister("r4")

# --- 1) find gp value ---
GPVAL = 0xFEBFC000  # resolved from crt0 (0x10C82)
# (a) symbol table
st = currentProgram.getSymbolTable()
for nm in ('_gp', '__gp', 'gp', '_gp_HI', '__gp__'):
    it = st.getSymbols(nm)
    while it.hasNext():
        s = it.next()
        GPVAL = s.getAddress().getOffset()
        print('[gp] from symbol %s = 0x%08x' % (nm, GPVAL))
        break
    if GPVAL: break
# (b) scan instructions near entry that load r4 with movhi/movea/mov imm
if GPVAL is None and gp is not None:
    # walk instructions, track per-register constant from movhi+movea into gp
    from collections import defaultdict
    ins_it = listing.getInstructions(True)
    hi = {}
    cnt = 0
    while ins_it.hasNext() and cnt < 20000:
        ins = ins_it.next(); cnt += 1
        mn = ins.getMnemonicString()
        objs = ins.getResultObjects()
        if not objs:
            continue
        out = objs[0]
        if not isinstance(out, Register):
            continue
        rname = out.getName()
        try:
            sc = ins.getScalar(0)
            val = sc.getUnsignedValue() if sc else None
        except Exception:
            val = None
        if mn == 'movhi' and val is not None:
            hi[rname] = (val << 16) & 0xFFFFFFFF
        elif mn in ('movea', 'add', 'ori', 'addi') and val is not None and rname in hi:
            cand = (hi[rname] + val) & 0xFFFFFFFF
            if out.getName() == gp.getName() or rname == gp.getName():
                if 0xFE000000 <= cand < 0xFF000000:
                    GPVAL = cand
                    print('[gp] from movhi/%s into %s = 0x%08x @ %s' % (mn, rname, cand, ins.getAddress()))
                    break
        elif mn == 'mov' and val is not None and rname == gp.getName() and 0xFE000000 <= (val & 0xFFFFFFFF) < 0xFF000000:
            GPVAL = val & 0xFFFFFFFF
            print('[gp] from mov imm into gp = 0x%08x @ %s' % (GPVAL, ins.getAddress()))
            break

if GPVAL is not None and gp is not None:
    from ghidra.program.model.lang import RegisterValue
    import java.math.BigInteger as BigInteger
    rv = RegisterValue(gp, BigInteger.valueOf(GPVAL))
    try:
        ctx.setRegisterValue(currentProgram.getMinAddress(), currentProgram.getMaxAddress(), rv)
        print('[gp] set gp context = 0x%08x program-wide' % GPVAL)
    except Exception as e:
        print('[gp] could not set context: %s' % e)
    print('[probe] gp-0x5bd2 = 0x%08x  (rev-cut engage signal)' % ((GPVAL - 0x5bd2) & 0xFFFFFFFF))
    print('[probe] gp-0x5bd6 = 0x%08x' % ((GPVAL - 0x5bd6) & 0xFFFFFFFF))
    print('[probe] gp-0x5c10 = 0x%08x' % ((GPVAL - 0x5c10) & 0xFFFFFFFF))
else:
    print('[gp] NOT FOUND - gp-relative will stay unresolved')

# --- 2) decompile + resolve call args (deeper) ---
dif = DecompInterface(); dif.openProgram(currentProgram); mon = ConsoleTaskMonitor()

def resolve(vn, depth=0):
    if vn is None or depth > 10:
        return None
    if vn.isConstant():
        return ('C', vn.getOffset() & 0xFFFFFFFF)
    a = vn.getAddress()
    if a is not None and a.isMemoryAddress() and not a.isStackAddress():
        return ('M', a.getOffset() & 0xFFFFFFFF)
    d = vn.getDef()
    if d is None:
        return None
    op = d.getMnemonic(); ins = d.getInputs()
    if op == 'LOAD' and len(ins) >= 2:
        r = resolve(ins[1], depth + 1)
        if r and r[0] == 'C':
            return ('M', r[1])
        return r
    if op in ('COPY', 'CAST', 'INT_ZEXT', 'INT_SEXT', 'INT_2COMP', 'SUBPIECE', 'INDIRECT'):
        return resolve(ins[0], depth + 1)
    if op == 'MULTIEQUAL':
        for i in ins:
            r = resolve(i, depth + 1)
            if r:
                return r
        return None
    if op in ('INT_ADD', 'PTRADD', 'PTRSUB', 'INT_SUB') and len(ins) >= 2:
        ra = resolve(ins[0], depth + 1); rb = resolve(ins[1], depth + 1)
        if ra and rb and ra[0] == 'C' and rb[0] == 'C':
            v = (ra[1] + rb[1]) if op != 'INT_SUB' else (ra[1] - rb[1])
            return ('C', v & 0xFFFFFFFF)
        if ra and ra[0] == 'M':
            return ra
        if rb and rb[0] == 'M':
            return rb
        return ra or rb
    return None

fh = open(outfile, 'w'); n = 0; cnt = 0
it = fm.getFunctions(True)
while it.hasNext():
    f = it.next(); cnt += 1
    try:
        res = dif.decompileFunction(f, 45, mon)
        hf = res.getHighFunction() if res else None
        if hf is None:
            continue
        ent = f.getEntryPoint().getOffset()
        ops = hf.getPcodeOps()
        while ops.hasNext():
            op = ops.next()
            if op.getMnemonic() not in ('CALL', 'CALLIND'):
                continue
            site = op.getSeqnum().getTarget().getOffset()
            ins = op.getInputs()
            tgt = ins[0]
            tgts = ('%x' % tgt.getAddress().getOffset()) if tgt.isAddress() else 'IND'
            for i in range(1, len(ins)):
                r = resolve(ins[i])
                if r is None:
                    continue
                fh.write('%x\t%x\t%s\t%d\t%s:%x\n' % (ent, site, tgts, i - 1, r[0], r[1]))
                n += 1
    except Exception:
        pass
fh.close()
print('[DumpLookups2] decompiled %d funcs, wrote %d resolved args to %s' % (cnt, n, outfile))
