import os
import re
import hashlib

SRC_DIR = "output/ceto_fourier_programs"
OUT_DIR = "output/ceto_fourier_stages_v2"
os.makedirs(OUT_DIR, exist_ok=True)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def find_stage(lines, stage):
    pattern = re.compile(
        rf"^\s*#\s*ifdef\s+{stage}\s*$"
    )

    start = None
    for i, line in enumerate(lines):
        if pattern.match(line):
            start = i
            break

    if start is None:
        return None

    depth = 0

    for i in range(start, len(lines)):
        s = lines[i].strip()

        if re.match(r"#\s*(if|ifdef|ifndef)\b", s):
            depth += 1
        elif re.match(r"#\s*endif\b", s):
            depth -= 1

            if depth == 0:
                return lines[start + 1:i]

    raise ValueError(f"Unclosed {stage} block")

for entry in range(8):
    path = f"{SRC_DIR}/platform15_entry_{entry}.glsl"

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    # Earlier extraction removed the original outer VERTEX directive.
    source = "#ifdef VERTEX\n" + source

    lines = source.splitlines(keepends=True)

    print(f"\nENTRY {entry}")

    for stage in ("VERTEX", "FRAGMENT"):
        body = find_stage(lines, stage)

        if body is None:
            print("MISSING:", stage)
            continue

        code = "".join(body).lstrip()
        data = code.encode("utf-8")

        out = f"{OUT_DIR}/entry_{entry}_{stage.lower()}.glsl"

        with open(out, "wb") as f:
            f.write(data)

        text = code

        uniforms = sorted(set(re.findall(
            r"\buniform\s+\w+\s+(\w+)",
            text
        )))

        samplers = sorted(set(re.findall(
            r"\buniform\s+\w*sampler\w*\s+(\w+)",
            text
        )))

        print(f"  {stage}: PASS")
        print("  SIZE:", len(data))
        print("  SHA256:", sha(data))
        print("  VERSION:", next(
            (x.strip() for x in text.splitlines()
             if x.strip().startswith("#version")),
            "NOT FOUND"
        ))
        print("  MAIN COUNT:", text.count("void main"))
        print("  UNIFORMS:", uniforms)
        print("  SAMPLERS:", samplers)
        print("  FILE:", out)

print("\nOUTPUT:", OUT_DIR)
