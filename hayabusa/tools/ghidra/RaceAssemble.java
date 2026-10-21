// Assemble the TPS spare-reader removal with the project's own V850E3V5 language.
import ghidra.app.script.GhidraScript;
import ghidra.app.plugin.assembler.*;
import ghidra.program.model.address.Address;
import java.io.*;
public class RaceAssemble extends GhidraScript {
    public void run() throws Exception {
        Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x453b0);
        Assembler assembler = Assemblers.getAssembler(currentProgram);
        byte[] bytes = assembler.assembleLine(a, "cmp 0x2,r28");
        try (PrintWriter out = new PrintWriter(new FileWriter(getScriptArgs()[0]))) {
            out.println("Language: " + currentProgram.getLanguageID());
            out.println("Program SHA256: " + currentProgram.getExecutableSHA256());
            out.println("Address: " + a);
            out.println("Original: " + currentProgram.getListing().getInstructionAt(a));
            out.print("cmp 0x2,r28 bytes: ");
            for (byte b : bytes) out.printf("%02x", b & 255);
            out.println();
        }
    }
}
