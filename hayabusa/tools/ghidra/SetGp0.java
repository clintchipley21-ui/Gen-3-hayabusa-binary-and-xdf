// Pin gp=0 and tp=0 across the whole program so the decompiler folds the
// cosmetic "+ unaff_gp" and resolves gp/tp-relative references to absolute
// addresses. (No explicit gp load exists in the app code -> gp is 0 at app level.)
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import java.math.BigInteger;

public class SetGp0 extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address min = currentProgram.getMinAddress();
        Address max = currentProgram.getMaxAddress();
        for (String name : new String[]{"gp", "tp"}) {
            Register r = currentProgram.getRegister(name);
            if (r != null) {
                currentProgram.getProgramContext().setValue(r, min, max, BigInteger.ZERO);
                println("set " + name + "=0 over " + min + ".." + max);
            }
        }
    }
}
