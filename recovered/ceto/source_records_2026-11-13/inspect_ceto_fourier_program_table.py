import os
import struct
import UnityPy
import lz4.block

ROOT = "/sdcard/Download/3zip/Stranded Deep/Stranded_Deep_Data"
TARGET_ID = 178

env = UnityPy.load(os.path.join(ROOT, "sharedassets0.assets"))

def inspect_payload(label, raw):
    print("\n" + "=" * 65)
    print(label)
    print("SIZE:", len(raw))
    print("HEADER:", raw[:112].hex())

    count = struct.unpack_from("<I", raw, 0)[0]
    print("ENTRY COUNT:", count)

    # Test the suspected 12-byte table layout.
    table_end = 4 + count * 12
    print("TABLE END:", table_end)

    if table_end > len(raw):
        print("ERROR: table exceeds payload")
        return

    for i in range(count):
        pos = 4 + i * 12
        offset, size, extra = struct.unpack_from("<III", raw, pos)

        valid = (
            offset >= table_end
            and size > 0
            and offset + size <= len(raw)
        )

        print(f"\nENTRY {i}")
        print("  OFFSET:", offset)
        print("  SIZE:", size)
        print("  EXTRA:", extra)
        print("  RANGE VALID:", valid)

        if not valid:
            continue

        chunk = raw[offset:offset + size]
        print("  PREFIX:", chunk[:32].hex())

        if chunk.startswith(b"DXBC"):
            print("  TYPE: DXBC")
        elif b"#version" in chunk[:256]:
            print("  TYPE: GLSL")
        else:
            print("  TYPE: OTHER")

        preview = bytes(
            b if 32 <= b < 127 or b in (9, 10, 13) else 46
            for b in chunk[:240]
        )
        print("  PREVIEW:")
        print(preview.decode("ascii", errors="replace"))

for obj in env.objects:
    if obj.path_id != TARGET_ID or obj.type.value != 48:
        continue

    data = obj.read()
    blob = bytes(data.compressedBlob)

    for i in range(len(data.offsets)):
        offset = data.offsets[i][0]
        clen = data.compressedLengths[i][0]
        dlen = data.decompressedLengths[i][0]

        segment = blob[offset:offset + clen]
        raw = lz4.block.decompress(
            segment,
            uncompressed_size=dlen
        )

        inspect_payload(f"PAYLOAD {i} PLATFORM {data.platforms[i]}", raw)

    break
