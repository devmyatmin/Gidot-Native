import re
import dnfile
from collections import Counter

DLL = "/sdcard/Download/3zip/Stranded Deep/Stranded_Deep_Data/Managed/Assembly-CSharp.dll"
SRC = "logic/fourier_support_il.txt"
REPORT = "logic/fourier_support_token_report.txt"
OUT_IL = "logic/fourier_support_il_resolved.txt"

pe = dnfile.dnPE(DLL)

with open(SRC, encoding="utf-8") as f:
    source = f.read()

def s(value):
    if value is None:
        return "?"
    try:
        v = getattr(value, "value", value)
        return str(v)
    except Exception:
        return str(value)

def get_row(entry):
    return getattr(entry, "row", entry)

def type_name(row):
    if row is None:
        return "?"
    ns = s(getattr(row, "TypeNamespace", ""))
    name = s(getattr(row, "TypeName", ""))
    if not name or name == "?":
        name = s(getattr(row, "Name", "?"))
    return (ns + "." + name).strip(".")

def row_table(row):
    if row is None:
        return "?"
    return type(row).__name__.replace("Row", "")

# Build declaring-type maps for MethodDef and Field rows.
method_owner = {}
field_owner = {}

for td in pe.net.mdtables.TypeDef.rows:
    owner = type_name(td)

    for entry in getattr(td, "MethodList", []):
        row = get_row(entry)
        if row is not None:
            method_owner[id(row)] = owner

    for entry in getattr(td, "FieldList", []):
        row = get_row(entry)
        if row is not None:
            field_owner[id(row)] = owner

def resolve_coded_parent(parent):
    row = get_row(parent)
    if row is None:
        return "parent=?"

    kind = row_table(row)

    if kind == "TypeDef":
        return type_name(row)
    if kind == "TypeRef":
        return type_name(row)
    if kind == "MethodDef":
        owner = method_owner.get(id(row), "?")
        return f"{owner}::{s(row.Name)}"
    if kind == "TypeSpec":
        return "TypeSpec"
    return f"{kind}:{s(getattr(row, 'Name', '?'))}"

def resolve_token(token):
    table = (token >> 24) & 0xFF
    rid = token & 0xFFFFFF

    if table == 0x70:
        return f"USERSTRING(offset=0x{rid:X})"

    table_map = {
        0x01: "TypeRef",
        0x02: "TypeDef",
        0x04: "Field",
        0x06: "MethodDef",
        0x0A: "MemberRef",
        0x1B: "TypeSpec",
        0x2B: "MethodSpec",
    }

    name = table_map.get(table)
    if not name:
        return f"UNKNOWN_TABLE_0x{table:02X}(RID={rid})"

    md = getattr(pe.net.mdtables, name, None)
    if md is None or rid < 1 or rid > len(md.rows):
        return f"{name}(RID={rid}, ROW_UNAVAILABLE)"

    row = md.rows[rid - 1]

    if table == 0x01:
        return f"TYPE {type_name(row)}"

    if table == 0x02:
        return f"TYPE {type_name(row)}"

    if table == 0x04:
        owner = field_owner.get(id(row), "?")
        return f"FIELD {owner}::{s(row.Name)}"

    if table == 0x06:
        owner = method_owner.get(id(row), "?")
        return f"METHOD {owner}::{s(row.Name)} [RVA=0x{int(row.Rva):X}]"

    if table == 0x0A:
        parent = resolve_coded_parent(row.Class)
        return f"MEMBER {parent}::{s(row.Name)}"

    if table == 0x1B:
        return f"TYPESPEC RID={rid}"

    if table == 0x2B:
        method = resolve_coded_parent(row.Method)
        return f"METHODSPEC {method}"

    return f"{name}(RID={rid})"

tokens = [
    int(x, 16)
    for x in re.findall(r"token\(0x([0-9A-Fa-f]{8})\)", source)
]

unique = sorted(set(tokens))
counts = Counter(tokens)

lines = []
lines.append("CETO TOKEN RESOLUTION REPORT")
lines.append(f"TOTAL REFERENCES: {len(tokens)}")
lines.append(f"UNIQUE TOKENS: {len(unique)}")
lines.append("")

resolved = {}

for token in unique:
    result = resolve_token(token)
    resolved[token] = result
    lines.append(
        f"0x{token:08X} | COUNT={counts[token]:4d} | {result}"
    )

with open(REPORT, "w", encoding="utf-8") as f:
    f.write("\\n".join(lines) + "\\n")

def replace_token(match):
    token = int(match.group(1), 16)
    result = resolved.get(token, resolve_token(token))
    return f"token(0x{token:08X}) [{result}]"

resolved_source = re.sub(
    r"token\(0x([0-9A-Fa-f]{8})\)",
    replace_token,
    source
)

with open(OUT_IL, "w", encoding="utf-8") as f:
    f.write(resolved_source)

print("CETO TOKEN RESOLUTION COMPLETE")
print("TOTAL REFERENCES:", len(tokens))
print("UNIQUE TOKENS:", len(unique))
print("METHODDEF:", sum(1 for t in unique if (t >> 24) == 0x06))
print("MEMBERREF:", sum(1 for t in unique if (t >> 24) == 0x0A))
print("FIELD:", sum(1 for t in unique if (t >> 24) == 0x04))
print("REPORT:", REPORT)
print("RESOLVED IL:", OUT_IL)
print()
print("TOP 40 RESOLVED TOKENS:")
for token in sorted(unique, key=lambda t: counts[t], reverse=True)[:40]:
    print(f"{counts[token]:4d}  0x{token:08X}  {resolved[token]}")
