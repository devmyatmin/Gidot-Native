import os
import hashlib
import struct
import UnityPy
import lz4.block

ROOT = "/sdcard/Download/3zip/Stranded Deep/Stranded_Deep_Data"
OUT = "output/ceto_fourier_programs"
os.makedirs(OUT, exist_ok=True)

env = UnityPy.load(os.path.join(ROOT, "sharedassets0.assets"))

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def extract_entries(raw, platform, count):
    table_start = 4
    table_end = table_start + count * 12

    for i in range(count):
        pos = table_start + i * 12
        offset, size, extra = struct.unpack_from("<III", raw, pos)
        chunk = raw[offset:offset + size]

        if len(chunk) != size:
            print("INVALID ENTRY:", platform, i)
            continue

        if platform == 4:
            marker = chunk.find(b"DXBC")
            if marker < 0:
                print("DXBC NOT FOUND:", i)
                continue

            dxbc = chunk[marker:]

            if len(dxbc) >= 32:
                declared_size = struct.unpack_from("<I", dxbc, 24)[0]
                if 32 <= declared_size <= len(dxbc):
                    dxbc = dxbc[:declared_size]

            path = f"{OUT}/platform4_entry_{i}.dxbc"
            with open(path, "wb") as f:
                f.write(dxbc)

            print(
                f"DXBC ENTRY {i}: offset={offset}, size={size}, "
                f"inner_offset={marker}, extracted={len(dxbc)}, "
                f"sha256={sha256(dxbc)}"
            )

        elif platform == 15:
            marker = chunk.find(b"#version")
            if marker < 0:
                print("GLSL SOURCE NOT FOUND:", i)
                continue

            source = chunk[marker:]
            source = source.split(b"\x00", 1)[0]

            path = f"{OUT}/platform15_entry_{i}.glsl"
            with open(path, "wb") as f:
                f.write(source)

            text = source.decode("utf-8", errors="replace")
            lines = text.splitlines()

            print(
                f"\nGLSL ENTRY {i}: offset={offset}, size={size}, "
                f"source_offset={marker}, source_size={len(source)}"
            )
            print("SHA256:", sha256(source))

            for line_no, line in enumerate(lines, 1):
                s = line.strip()
                if (
                    s.startswith("#version")
                    or s.startswith("#ifdef")
                    or s.startswith("#if ")
                    or s.startswith("#elif")
                    or s.startswith("#else")
                    or s.startswith("#endif")
                    or "void main" in s
                ):
                    print(f"  L{line_no}: {s[:180]}")

for obj in env.objects:
    if obj.path_id != 178 or obj.type.value != 48:
        continue

    data = obj.read()
    blob = bytes(data.compressedBlob)

    print("SHADER:", data.m_ParsedForm.m_Name)

    for i, platform in enumerate(data.platforms):
        offset = data.offsets[i][0]
        clen = data.compressedLengths[i][0]
        dlen = data.decompressedLengths[i][0]

        raw = lz4.block.decompress(
            blob[offset:offset + clen],
            uncompressed_size=dlen
        )

        count = struct.unpack_from("<I", raw, 0)[0]

        print(
            f"\nPLATFORM {platform}: "
            f"decompressed={len(raw)}, entries={count}"
        )

        extract_entries(raw, platform, count)

    break

print("\nOUTPUT DIRECTORY:", OUT)
