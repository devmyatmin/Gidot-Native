import os
import re
import hashlib

SRC_DIR = "output/ceto_fourier_programs"
OUT_DIR = "output/ceto_fourier_stages"
os.makedirs(OUT_DIR, exist_ok=True)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def extract_block(lines, start):
    depth = 0
    result = []

    for i in range(start, len(lines)):
        line = lines[i].strip()

        if re.match(r"#\s*(if|ifdef|ifndef)\b", line):
            depth += 1
        elif re.match(r"#\s*endif\b", line):
            depth -= 1

        result.append(lines[i])

        if depth == 0:
            return result, i + 1

    raise ValueError("Unclosed preprocessor block")

for entry in range(8):
    path = f"{SRC_DIR}/platform15_entry_{entry}.glsl"

    with open(path, "rb") as f:
        raw = f.read()

    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines(keepends=True)

    print(f"\nENTRY {entry}")
    print("SOURCE SIZE:", len(raw))
    print("SOURCE SHA256:", sha(raw))

    stages = {}

    for i, line in enumerate(lines):
        match = re.match(
            r"\s*#\s*ifdef\s+(VERTEX|FRAGMENT)\b",
            line
        )

        if not match:
            continue

        stage = match.group(1)

        if stage in stages:
            continue

        block, end = extract_block(lines, i)
        stages[stage] = block

    for stage in ("VERTEX", "FRAGMENT"):
        if stage not in stages:
            print("MISSING STAGE:", stage)
            continue

        block = "".join(stages[stage]).encode("utf-8")
        out = f"{OUT_DIR}/entry_{entry}_{stage.lower()}.glsl"

        with open(out, "wb") as f:
            f.write(block)

        code = block.decode("utf-8", errors="replace")

        uniforms = sorted(set(re.findall(
            r"\buniform\s+\w+\s+(\w+)",
            code
        )))

        samplers = sorted(set(re.findall(
            r"\buniform\s+\w*sampler\w*\s+(\w+)",
            code
        )))

        print(f"  {stage}: {len(block)} bytes")
        print("  SHA256:", sha(block))
        print("  MAIN:", code.count("void main"))
        print("  UNIFORMS:", uniforms)
        print("  SAMPLERS:", samplers)
        print("  FILE:", out)

print("\nOUTPUT:", OUT_DIR)
