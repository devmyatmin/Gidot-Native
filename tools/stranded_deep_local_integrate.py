#!/usr/bin/env python3
"""Stage existing Stranded Deep C# assemblies for Godot; source files stay read-only."""
from __future__ import annotations
import argparse, csv, hashlib, json, shutil, sys
from pathlib import Path
from datetime import datetime, timezone

def digest(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def copy_once(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if dst.stat().st_size == src.stat().st_size and digest(dst) == digest(src):
            return "ALREADY_IDENTICAL"
        return "DESTINATION_CONFLICT"
    shutil.copy2(src, dst)
    return "COPIED"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--threezip", required=True)
    ap.add_argument("--godot", required=True)
    a = ap.parse_args()
    data, zroot, godot = [Path(x).expanduser().resolve() for x in (a.data, a.threezip, a.godot)]
    managed, logic = data / "Managed", zroot / "Libraries" / "GameLogic"
    if not managed.is_dir(): sys.exit(f"ERROR: Managed folder not found: {managed}")
    if not logic.is_dir(): sys.exit(f"ERROR: Libraries/GameLogic not found: {logic}")
    if not godot.is_dir(): sys.exit(f"ERROR: Godot project not found: {godot}")

    root = godot / "SourceLogic" / "AssemblyIntegration"
    destinations = {
        "REWRITTEN_GODOT_CSHARP_CANDIDATE": root / "GodotLogicCandidates",
        "ORIGINAL_GAME_ASSEMBLY_REFERENCE": root / "OriginalUnityReferences",
        "MANAGED_DEPENDENCY_REFERENCE": root / "ManagedDependencyReferences",
        "UNITY_ENGINE_REFERENCE": root / "ManagedDependencyReferences",
    }
    report_dir = root / "Reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    sources = []
    for p in sorted(logic.rglob("*.dll")):
        if p.is_file(): sources.append(("REWRITTEN_GODOT_CSHARP_CANDIDATE", p, logic))
    for p in sorted(managed.rglob("*.dll")):
        if not p.is_file(): continue
        n = p.name.lower()
        kind = ("ORIGINAL_GAME_ASSEMBLY_REFERENCE" if n in ("assembly-csharp.dll", "assembly-csharp-firstpass.dll")
                else "UNITY_ENGINE_REFERENCE" if n.startswith("unityengine") or n.startswith("unity")
                else "MANAGED_DEPENDENCY_REFERENCE")
        sources.append((kind, p, managed))

    rows, errors = [], []
    for kind, src, base in sources:
        dst = destinations[kind] / src.relative_to(base)
        try:
            rows.append({"classification":kind, "source":str(src), "staged":str(dst),
                         "file":src.name, "size_bytes":src.stat().st_size,
                         "sha256":digest(src), "status":copy_once(src,dst)})
        except Exception as e:
            errors.append({"source":str(src), "error":repr(e)})

    by_name = {}
    for r in rows: by_name.setdefault(r["file"].lower(), []).append(r)
    comparisons = []
    for name, items in sorted(by_name.items()):
        if len(items) > 1:
            comparisons.append({"file":name, "same_binary":len({x["sha256"] for x in items}) == 1,
                                "copies":[{"classification":x["classification"],"source":x["source"],
                                           "sha256":x["sha256"],"size_bytes":x["size_bytes"]} for x in items]})

    stamp = datetime.now(timezone.utc).isoformat()
    fields = ["classification","source","staged","file","size_bytes","sha256","status"]
    with (report_dir / "assembly_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    counts = {
        "rewritten_logic_dlls":sum(x["classification"] == "REWRITTEN_GODOT_CSHARP_CANDIDATE" for x in rows),
        "original_game_assemblies":sum(x["classification"] == "ORIGINAL_GAME_ASSEMBLY_REFERENCE" for x in rows),
        "managed_dependencies":sum(x["classification"] in ("UNITY_ENGINE_REFERENCE","MANAGED_DEPENDENCY_REFERENCE") for x in rows),
        "destination_conflicts":sum(x["status"] == "DESTINATION_CONFLICT" for x in rows),
        "errors":len(errors)}
    report = {"version":"1.0.0","generated_utc":stamp,"source_data":str(data),
              "source_rewritten_logic":str(logic),"godot_project":str(godot),
              "counts":counts,"same_name_comparisons":comparisons,"errors":errors,
              "note":"DLLs are staged and hashed; this does not rewrite APIs or certify runtime compatibility."}
    (report_dir / "assembly_integration_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    summary = ("STRANDED DEEP / GODOT ASSEMBLY INTEGRATION\n"
               f"Rewritten C# candidate DLLs: {counts['rewritten_logic_dlls']}\n"
               f"Original game assembly references: {counts['original_game_assemblies']}\n"
               f"Managed dependency references: {counts['managed_dependencies']}\n"
               f"Destination conflicts: {counts['destination_conflicts']}\nErrors: {counts['errors']}\n"
               f"Reports: {report_dir}\nSource files modified: NO\n")
    (report_dir / "assembly_integration_summary.txt").write_text(summary,encoding="utf-8")
    print(summary)
    return 1 if counts["destination_conflicts"] or errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
