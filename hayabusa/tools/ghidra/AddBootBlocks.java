// Pre-analysis: add uninitialized RAM / peripheral blocks so RH850 boot code's
// data references resolve instead of dead-ending. Boot image itself is 0x0..0xFFFF.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;

public class AddBootBlocks extends GhidraScript {
    private void mk(Memory mem, String name, long start, long len) throws Exception {
        Address a = toAddr(start);
        for (MemoryBlock b : mem.getBlocks()) {
            if (b.contains(a)) { println("skip "+name+" (overlaps "+b.getName()+")"); return; }
        }
        MemoryBlock blk = mem.createUninitializedBlock(name, a, len, false);
        blk.setRead(true); blk.setWrite(true); blk.setExecute(false);
        blk.setVolatile(name.startsWith("IO"));
        println("added "+name+" @ "+a+" len=0x"+Long.toHexString(len));
    }
    @Override
    public void run() throws Exception {
        Memory mem = currentProgram.getMemory();
        // RH850/E1x local RAM (als.s referenced 0xFEBFE000); cover the global+local RAM window
        mk(mem, "RAM_local",  0xFEBF0000L, 0x00210000L);  // 0xFEBF0000..0xFEDFFFFF
        // Peripheral / SFR space
        mk(mem, "IO_periph",  0xFF000000L, 0x00400000L);  // 0xFF000000..0xFF3FFFFF
        mk(mem, "IO_periph2", 0xFFC00000L, 0x00400000L);  // 0xFFC00000..0xFFFFFFFF
    }
}
