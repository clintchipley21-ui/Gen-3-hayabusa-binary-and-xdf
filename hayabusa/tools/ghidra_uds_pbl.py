# Ghidra post-script: find the PBL validation path and the UDS/OBD reflash handlers
# in the 5JCUSJ40 full dump (RH850/F1L). Targets: what the Primary Boot Loader checks
# before jumping to the app, and the UDS services used for on-vehicle reprogramming
# (security-access seed/key is the gate).
#
# Run after import/auto-analyze (RH850:LE:32 @ 0x0):
#   analyzeHeadless <proj> busa5jcu \
#       -import 5JCUSJ40-full.bin -loader BinaryLoader -loader-baseAddr 0x0 \
#       -processor "RH850:LE:32:default" \
#       -postScript ghidra_uds_pbl.py <out_dir>
#
# Writes <out_dir>/uds_pbl_report.txt and per-handler decompilation files.
# @category Suzuki
import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.app.cmd.disassemble import DisassembleCommand

args = getScriptArgs()
out_dir = args[0] if args else os.getcwd()
prog = currentProgram
af = prog.getAddressFactory().getDefaultAddressSpace()
fm = prog.getFunctionManager()
mon = ConsoleTaskMonitor()
ifc = DecompInterface(); ifc.openProgram(prog)
rep = open(os.path.join(out_dir, "uds_pbl_report.txt"), "w")

def addr(x): return af.getAddress(x)
def w(s): rep.write(s + "\n")

# ---- 1. make sure boot/entry code is disassembled, then dump it ----
for start in (0x0, 0x3764, 0x3AF0, 0x10000):
    try:
        DisassembleCommand(addr(start), None, True).applyTo(prog, mon)
    except Exception as e:
        w("disasm 0x%X failed: %s" % (start, e))

listing = prog.getListing()
for start in (0x0, 0x3764, 0x3AF0, 0x10000):
    w("\n== disasm from 0x%X (first 80 instr) ==" % start)
    ins = listing.getInstructionAt(addr(start))
    k = 0
    while ins is not None and k < 80:
        w("0x%08x  %s" % (ins.getAddress().getOffset(), ins.toString()))
        ins = ins.getNext(); k += 1

# ---- 2. scan every function for UDS service-ID immediates + integrity-field addresses ----
# UDS (ISO 14229) request SIDs we care about for reprogramming + the field addresses.
UDS = {0x10: "DiagSessionControl", 0x11: "ECUReset", 0x27: "SecurityAccess (seed/key)",
       0x28: "CommunicationControl", 0x2E: "WriteDataByIdentifier", 0x31: "RoutineControl (erase)",
       0x34: "RequestDownload", 0x36: "TransferData", 0x37: "RequestTransferExit",
       0x3E: "TesterPresent", 0x85: "ControlDTCSetting"}
FIELD = {0x1FFAFE: "field-1 CRC", 0x1FFEF8: "field-3", 0x1FFEF0: "field-3 descriptor",
         0xFFFC: "boot-block-end word"}

def scalars_in(fn):
    vals = set()
    it = listing.getInstructions(fn.getBody(), True)
    while it.hasNext():
        ins = it.next()
        for i in range(ins.getNumOperands()):
            for obj in ins.getOpObjects(i):
                try:
                    v = obj.getValue() if hasattr(obj, "getValue") else None
                    if v is not None: vals.add(int(v) & 0xFFFFFFFF)
                except Exception:
                    pass
    return vals

uds_hits = {}   # sid -> [func addrs]
field_hits = {} # field addr -> [func addrs]
for fn in fm.getFunctions(True):
    vs = scalars_in(fn)
    ep = fn.getEntryPoint().getOffset()
    for sid in UDS:
        if sid in vs:
            uds_hits.setdefault(sid, []).append(ep)
    for fa in FIELD:
        if fa in vs:
            field_hits.setdefault(fa, []).append(ep)

w("\n\n== UDS service-ID immediates found in functions ==")
for sid in sorted(UDS):
    fns = uds_hits.get(sid, [])
    w("  0x%02X %-28s : %d function(s) %s"
      % (sid, UDS[sid], len(fns), ", ".join("0x%08x" % a for a in fns[:12])))

w("\n== Integrity-field address references ==")
for fa in sorted(FIELD):
    fns = field_hits.get(fa, [])
    w("  0x%06X %-22s : %s" % (fa, FIELD[fa], ", ".join("0x%08x" % a for a in fns[:12]) or "none"))

# ---- 3. decompile the most interesting handlers (security access + download + field-3) ----
def decompile_to(ep, tag):
    fn = fm.getFunctionAt(addr(ep))
    if fn is None: return
    res = ifc.decompileFunction(fn, 60, mon)
    path = os.path.join(out_dir, "fn_%s_%08x.c" % (tag, ep))
    with open(path, "w") as f:
        if res and res.decompileCompleted():
            f.write(res.getDecompiledFunction().getC())
        else:
            f.write("// decompile failed")
    w("  wrote %s" % os.path.basename(path))

w("\n== decompiling priority handlers ==")
for sid, tag in ((0x27, "secaccess"), (0x34, "reqdownload"), (0x36, "transfer"),
                 (0x31, "routine"), (0x10, "session")):
    for ep in uds_hits.get(sid, [])[:3]:
        decompile_to(ep, tag)
for fa, tag in ((0x1FFEF8, "field3"), (0x1FFAFE, "field1")):
    for ep in field_hits.get(fa, [])[:3]:
        decompile_to(ep, tag)

rep.close()
print("UDS/PBL report written to %s" % os.path.join(out_dir, "uds_pbl_report.txt"))
