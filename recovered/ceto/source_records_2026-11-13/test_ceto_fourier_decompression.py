import os
import hashlib
import UnityPy

ROOT = "/sdcard/Download/3zip/Stranded Deep/Stranded_Deep_Data"
TARGET_ID = 178

try:
    import lz4.block
except ImportError:
    print("ERROR: lz4 package missing")
    raise SystemExit(1)

env = UnityPy.load(os.path.join(ROOT, "sharedassets0.assets"))

for obj in env.objects:
    if obj.path_id != TARGET_ID or obj.type.value != 48:
        continue

    data = obj.read()
    blob = bytes(data.compressedBlob)

    print("SHADER:", data.m_ParsedForm.m_Name)
    print("BLOB SIZE:", len(blob))
    print("PLATFORMS:", data.platforms)

    for i, (offset, clen, dlen) in enumerate(zip(
        [x[0] for x in data.offsets],
        [x[0] for x in data.compressedLengths],
        [x[0] for x in data.decompressedLengths]
    )):
        segment = blob[offset:offset + clen]

        print("\nPAYLOAD:", i)
        print("OFFSET:", offset)
        print("COMPRESSED:", clen)
        print("EXPECTED DECOMPRESSED:", dlen)
        print("SHA256 COMPRESSED:", hashlib.sha256(segment).hexdigest())

        try:
            raw = lz4.block.decompress(
                segment,
                uncompressed_size=dlen
            )
            print("DECOMPRESS: PASS")
            print("ACTUAL SIZE:", len(raw))
            print("SHA256 RAW:", hashlib.sha256(raw).hexdigest())
            print("PREFIX:", raw[:32].hex())

            if raw.startswith(b"DXBC"):
                print("SIGNATURE: DXBC")
            elif raw.startswith(b"#version"):
                print("SIGNATURE: GLSL")
            else:
                print("SIGNATURE: OTHER")

            printable = bytes(
                b if 32 <= b < 127 or b in (9, 10, 13) else 46
                for b in raw[:500]
            )
            print("TEXT PREVIEW:")
            print(printable.decode("ascii", errors="replace"))

        except Exception as e:
            print("DECOMPRESS: FAILED")
            print("ERROR:", repr(e))

    print("\n=== SUBPROGRAM INDEX MAP ===")
    for pi, shader_pass in enumerate(data.m_ParsedForm.m_SubShaders[0].m_Passes):
        print("\nPASS", pi)
        print("  PLATFORMS:", shader_pass.m_Platforms)
        print("  PROGRAM MASK:", shader_pass.m_ProgramMask)

        for stage_name in (
            "progVertex", "progFragment",
            "progGeometry", "progHull"
        ):
            program = getattr(shader_pass, stage_name)
            for sub in program.m_SubPrograms:
                print(
                    " ", stage_name,
                    "BlobIndex:", sub.m_BlobIndex,
                    "GpuProgramType:", sub.m_GpuProgramType,
                    "HardwareTier:", sub.m_ShaderHardwareTier
                )
    break
