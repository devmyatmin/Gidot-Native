import os
import dnfile
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes

DLL = "/sdcard/Download/3zip/Stranded Deep/Stranded_Deep_Data/Managed/Assembly-CSharp.dll"
OUT = "logic/fourier_support_il.txt"

pe = dnfile.dnPE(DLL)

def val(x):
    return str(getattr(x, "value", x))

def row_of(x):
    return getattr(x, "row", x)

def typename(t):
    ns, name = val(t.TypeNamespace), val(t.TypeName)
    return f"{ns}.{name}" if ns else name

def extract(m, owner, lines):
    lines += [
        "\n" + "=" * 75,
        f"CLASS: {owner}",
        f"METHOD: {val(m.Name)}",
        f"RID: {pe.net.mdtables.MethodDef.rows.index(m)+1}",
        f"RVA: 0x{int(m.Rva):X}",
        f"SIGNATURE: {m.Signature}",
    ]
    if not m.Rva:
        lines.append("[NO METHOD BODY]")
        return
    try:
        body = CilMethodBody(
            CilMethodBodyReaderBytes(pe.get_data(int(m.Rva), 0x10000))
        )
        lines.append(f"CODE_SIZE: {body.code_size}")
        lines.append(f"INSTRUCTIONS: {len(body.instructions)}")
        for ins in body.instructions:
            op = ins.operand
            lines.append(
                f"IL_{ins.offset:04X}: {ins.opcode.name} "
                f"{op if op is not None else ''}"
            )
    except Exception as e:
        lines.append(f"DECODE_ERROR: {type(e).__name__}: {e}")

lines = ["FOURIER GPU SUPPORT EXTRACTION"]

# Extract all FourierGPU methods, including its constructor.
for t in pe.net.mdtables.TypeDef.rows:
    owner = typename(t)
    if owner == "Ceto.FourierGPU":
        for entry in t.MethodList:
            extract(row_of(entry), owner, lines)

# Extract RTUtility.MultiTargetBlit: MethodDef token 0x0600312A.
rid = 0x0600312A & 0xFFFFFF
m = pe.net.mdtables.MethodDef.rows[rid - 1]
extract(m, "Ceto.Common.Unity.Utility.RTUtility", lines)

# Resolve the user-string tokens seen in FourierGPU IL.
lines += ["\n" + "=" * 75, "USER STRING RESOLUTION"]
for token in [
    0x70015C48, 0x70015C8A, 0x70015CB4, 0x70015CD6,
    0x70015D3A, 0x70015D5C, 0x70015DC0, 0x70015DE2,
    0x70015E46
]:
    offset = token & 0x00FFFFFF
    try:
        item = pe.net.user_strings.get(offset)
        value = getattr(item, "value", item)
        lines.append(f"0x{token:08X} -> {value!r}")
    except Exception as e:
        lines.append(
            f"0x{token:08X} -> RESOLUTION_ERROR: {type(e).__name__}: {e}"
        )

os.makedirs("logic", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("FOURIER SUPPORT EXTRACTION COMPLETE")
print("OUTPUT:", OUT)
print("LINES:", len(lines))
print("BYTES:", os.path.getsize(OUT))
