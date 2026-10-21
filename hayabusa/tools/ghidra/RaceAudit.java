// Export instructions, references and decompilation for race-patch dependencies.
// Run against a COPY of the supplied busa project, with -noanalysis -readOnly.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;

public class RaceAudit extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("output text path required");
        DecompInterface dc = new DecompInterface();
        dc.openProgram(currentProgram);
        try (PrintWriter out = new PrintWriter(new FileWriter(args[0]))) {
            out.println("Program: " + currentProgram.getName());
            out.println("Language: " + currentProgram.getLanguageID());
            out.println("Executable SHA256: " + currentProgram.getExecutableSHA256());
            long[] funcs = {0x45320,0x4536c,0x453b8,0x4543e,0x454da,
                0x4558a,0x45e92,0x491bc,0x5171c,0x517b4,0x525ee,
                0x5db5e,0x5dc9a,0x69bc6,0x42384,0x742e2,
                0x3dbae,0x3ddb2,0x3e036,0x44996,0x484e0};
            for (long value : funcs) {
                Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value);
                Function f = currentProgram.getFunctionManager().getFunctionContaining(a);
                if (f == null) { out.println("NO FUNCTION " + a); continue; }
                out.println("\n=== " + f.getName() + " @ " + f.getEntryPoint() + " ===");
                InstructionIterator it = currentProgram.getListing().getInstructions(f.getBody(), true);
                while (it.hasNext()) {
                    Instruction ins = it.next();
                    out.println(ins.getAddress() + " " + ins);
                }
                DecompileResults r = dc.decompileFunction(f, 60, monitor);
                if (r.decompileCompleted()) out.println(r.getDecompiledFunction().getC());
                else out.println("DECOMPILE FAILED: " + r.getErrorMessage());
            }
            long[] refs = {0x17ebe4,0x154d8c,0xfef011caL,0xfef020e0L,
                0xfef020e1L,0xfef02090L,0x45338,0x4545e,0x52600,0x74302};
            for (long value : refs) {
                Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value);
                out.println("\nREFERENCES TO " + a);
                ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(a);
                while (it.hasNext()) out.println(it.next());
            }
        } finally { dc.dispose(); }
    }
}
