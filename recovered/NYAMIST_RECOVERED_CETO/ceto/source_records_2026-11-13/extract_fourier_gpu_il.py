import os
import dnfile
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes

DLL = (
    "/sdcard/Download/3zip/Stranded Deep/"
    "Stranded_Deep_Data/Managed/Assembly-CSharp.dll"
)

OUT = "logic/fourier_gpu_il.txt"

TARGET_RVAS = {
    0x7C418,
    0x7C450,
    0x7C48D,
    0x7C4C0,
    0x7C62C,
    0x7C734,
    0x7C8F0,
    0x7CAFC,
}

if not os.path.isfile(DLL):
    raise SystemExit("ERROR: Assembly-CSharp.dll not found")

pe = dnfile.dnPE(DLL)

owners = {}
for t in pe.net.mdtables.TypeDef.rows:
    ns = str(t.TypeNamespace or "")
    name = str(t.TypeName)
    owner = f"{ns}.{name}" if ns else name

    for entry in t.MethodList:
        m = getattr(entry, "row", entry)
        owners[id(m)] = owner

lines = ["CETO FOURIER GPU IL EXTRACTION"]
found = set()
failed = 0

for m in pe.net.mdtables.MethodDef.rows:
    rva = int(m.Rva)

    if rva not in TARGET_RVAS:
        continue

    found.add(rva)
    owner = owners.get(id(m), "?")
    name = str(m.Name)

    lines += [
        "",
        "=" * 80,
        f"CLASS: {owner}",
        f"METHOD: {name}",
        f"RVA: 0x{rva:X}",
        f"TOKEN: 0x06000000 | RID={pe.net.mdtables.MethodDef.rows.index(m)+1}",
    ]

    try:
        raw = pe.get_data(rva, 0x10000)
        body = CilMethodBody(CilMethodBodyReaderBytes(raw))

        lines.append(f"CODE_SIZE: {body.code_size}")
        lines.append(f"INSTRUCTION_COUNT: {len(body.instructions)}")

        for ins in body.instructions:
            operand = ins.operand
            lines.append(
                f"IL_{ins.offset:04X}: {ins.opcode.name} "
                f"{operand if operand is not None else ''}"
            )

    except Exception as e:
        failed += 1
        lines.append(f"DECODE_ERROR: {type(e).__name__}: {e}")

missing = sorted(TARGET_RVAS - found)

lines += [
    "",
    "EXTRACTION SUMMARY",
    f"TARGETS: {len(TARGET_RVAS)}",
    f"FOUND: {len(found)}",
    f"MISSING: {[hex(x) for x in missing]}",
    f"FAILED: {failed}",
]

os.makedirs("logic", exist_ok=True)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("\n".join(lines[-6:]))
print("OUTPUT:", OUT)
print("LINES:", len(lines))
print("BYTES:", os.path.getsize(OUT))
