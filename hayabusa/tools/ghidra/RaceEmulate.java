// Run the cross-compiled freestanding core's test in an emulator overlay only.
// args: flat-code-image load-address entry-address report-path
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import ghidra.program.model.address.*;
import java.nio.file.*;
import java.io.*;
public class RaceEmulate extends GhidraScript {
    public void run() throws Exception {
        String[] a=getScriptArgs();
        if (a.length != 4) throw new IllegalArgumentException("binary load entry report");
        long load=Long.decode(a[1]),entry=Long.decode(a[2]);
        long stop=0xcffffeL;
        EmulatorHelper emu=new EmulatorHelper(currentProgram);
        try {
            AddressSpace space=currentProgram.getAddressFactory().getDefaultAddressSpace();
            emu.writeMemory(space.getAddress(load),Files.readAllBytes(Path.of(a[0])));
            emu.writeRegister(emu.getPCRegister(),entry);
            emu.writeRegister(emu.getStackPointerRegister(),0xfebfef00L);
            emu.writeRegister("lp",stop);
            int steps=0;
            while (emu.getExecutionAddress().getOffset()!=stop && steps<2000000) {
                monitor.checkCancelled();
                if (!emu.step(monitor)) throw new Exception("emulator: "+emu.getLastError());
                ++steps;
            }
            long result=emu.readRegister("r10").longValue();
            try (PrintWriter out=new PrintWriter(new FileWriter(a[3]))) {
                out.println("Language: "+currentProgram.getLanguageID());
                out.println("Emulator overlay only; no ECU image patched or hardware actuated.");
                out.printf("load=0x%x entry=0x%x stop=0x%x\n",load,entry,stop);
                out.println("instructions stepped: "+steps);
                out.println("returned: "+(emu.getExecutionAddress().getOffset()==stop));
                out.println("self-test result (0=pass, otherwise C source line): "+result);
                out.println("physical I/O tested: false");
            }
            if (emu.getExecutionAddress().getOffset()!=stop || result!=0)
                throw new Exception("target self-test failed or instruction limit reached");
        } finally { emu.dispose(); }
    }
}
