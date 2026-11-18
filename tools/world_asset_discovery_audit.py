#!/usr/bin/env python3
# WORLD ONLY — discovery and extraction-gap audit. No extraction or source writes.
from __future__ import annotations
import argparse, csv, json, os, re, sys
from pathlib import Path
from collections import Counter, defaultdict

WORLD = re.compile(
    r"world|terrain|island|palm|tree|rock|cliff|shore|sand|coral|sea|ocean|water|"
    r"vegetation|grass|bush|plant|wreck|reef|beach|underwater|driftwood|shipwreck|"
    r"wave|sky|cloud|rain|storm|fog|mud|dirt|mountain|cave|landscape|seafort",
    re.I,
)
SKIP_SUFFIX = {".ress", ".resource", ".resS".lower()}

def read_csv(path):
    p = Path(path)
    if not p.is_file(): return []
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def first_existing(paths):
    for p in paths:
        if p and Path(p).exists(): return Path(p).resolve()
    return None

def find_source(explicit):
    if explicit: return Path(explicit).expanduser().resolve()
    candidates = [
        "/sdcard/Download/Stranded Deep/Stranded_Deep_Data",
        "/storage/emulated/0/Download/Stranded Deep/Stranded_Deep_Data",
        "/sdcard/Download/3zip/Stranded Deep/Stranded_Deep_Data",
        "/storage/emulated/0/Download/3zip/Stranded Deep/Stranded_Deep_Data",
    ]
    return first_existing(candidates)

def find_repo(explicit):
    if explicit: return Path(explicit).expanduser().resolve()
    home = Path.home()
    return first_existing([home / "Gidot-Native", "/sdcard/Download/Gidot-Native",
                           "/storage/emulated/0/Download/Gidot-Native"])

def find_output(explicit):
    if explicit: return Path(explicit).expanduser().resolve()
    candidates = [
        "/sdcard/stranded_native_port_output/run_20261112_094649",
        "/storage/emulated/0/stranded_native_port_output/run_20261112_094649",
        "/sdcard/Download/STRANDED_RECOVERED",
    ]
    return first_existing(candidates)

def object_name(obj):
    try:
        data = obj.read()
        for key in ("m_Name", "name"):
            value = getattr(data, key, None)
            if isinstance(value, str) and value.strip(): return value.strip()
        return type(data).__name__
    except Exception as e:
        return "", str(e)

def scan_unity(source):
    try:
        import UnityPy
    except Exception as e:
        raise RuntimeError("UnityPy import failed. Run this script in the Ubuntu/proot Python environment with UnityPy installed: " + str(e))
    found, errors = [], []
    containers = sorted(p for p in source.rglob("*")
                        if p.is_file() and p.suffix.lower() == ".assets")
    if not containers:
        raise RuntimeError("No *.assets containers found under: " + str(source))
    for container in containers:
        try:
            env = UnityPy.load(str(container))
            for obj in env.objects:
                try:
                    typ = getattr(obj.type, "name", str(obj.type))
                    name, read_error = object_name(obj)
                    rec = {
                        "source_container": str(container),
                        "class_id": getattr(obj, "type", None).value if hasattr(getattr(obj, "type", None), "value") else typ,
                        "object_type": typ,
                        "path_id": str(getattr(obj, "path_id", "")),
                        "name": name or "",
                        "byte_size": getattr(obj, "byte_size", ""),
                        "read_error": read_error or "",
                    }
                    found.append(rec)
                except Exception as e:
                    errors.append({"source_container": str(container), "path_id": str(getattr(obj, "path_id", "")),
                                   "error": repr(e)})
        except Exception as e:
            errors.append({"source_container": str(container), "error": repr(e)})
    return found, errors, containers

def file_index(root):
    out = defaultdict(list)
    if not root or not root.exists(): return out
    for p in root.rglob("*"):
        if p.is_file():
            m = re.search(r"(?:mesh_|texture_|tex_)?(-?\d+)", p.name, re.I)
            if m: out[m.group(1)].append(str(p))
    return out

def main():
    ap = argparse.ArgumentParser(description="World-only Unity asset discovery and extraction-gap audit")
    ap.add_argument("--source", help="Stranded_Deep_Data directory")
    ap.add_argument("--repo", help="Local Gidot-Native checkout")
    ap.add_argument("--output", help="Existing extraction output root (read-only)")
    ap.add_argument("--report-dir", help="Report output directory; default /sdcard/Download/godot/Reports/WorldAudit")
    args = ap.parse_args()

    source = find_source(args.source)
    repo = find_repo(args.repo)
    existing = find_output(args.output)
    if not source or not source.is_dir():
        ap.error("Original Stranded_Deep_Data folder not found. Pass --source with its exact path.")
    if not repo or not repo.is_dir():
        ap.error("Local Gidot-Native checkout not found. Pass --repo with its exact path.")
    report_dir = Path(args.report_dir or "/sdcard/Download/godot/Reports/WorldAudit").expanduser()
    report_dir.mkdir(parents=True, exist_ok=True)

    mesh_csv = repo / "01_MESH_ASSETS/mesh_inventory_named.csv"
    index_csv = repo / "01_MESH_ASSETS/mesh_index_validation_all_v2.csv"
    geom_csv = repo / "01_MESH_ASSETS/reconstructed_v5/geometry_validation_report.csv"
    mesh_assign_csv = repo / "Github/material_v1/mesh_material_assignments_v4.csv"
    tex_csv = repo / "Github/textures.csv"
    tex_map_csv = repo / "Github/material_v1/texture_mapping_verified_v2.csv"

    required = [mesh_csv, index_csv, geom_csv, mesh_assign_csv, tex_csv, tex_map_csv]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        ap.error("Required existing GitHub audit records missing locally: " + "; ".join(missing))

    mesh_rows, index_rows, geom_rows = map(read_csv, [mesh_csv, index_csv, geom_csv])
    assign_rows, texture_rows, texmap_rows = map(read_csv, [mesh_assign_csv, tex_csv, tex_map_csv])

    mesh_by_id = {r["PathID"]: r for r in mesh_rows}
    index_by_id = {r["PathID"]: r for r in index_rows}
    geom_by_name = {r["OBJ"]: r for r in geom_rows}
    world_mesh = {k:v for k,v in mesh_by_id.items() if WORLD.search(v.get("MeshName",""))}
    assign_by_mesh = defaultdict(list)
    for r in assign_rows:
        if r.get("mesh_path_id") in world_mesh: assign_by_mesh[r["mesh_path_id"]].append(r)
    world_materials = {r.get("material_path_id","") for rows in assign_by_mesh.values() for r in rows}
    world_texmaps = [r for r in texmap_rows if r.get("material_path_id") in world_materials and r.get("result") == "MATCH"]
    texture_by_id = {r.get("PathID",""):r for r in texture_rows}
    world_texture_ids = {r.get("texture_path_id","") for r in world_texmaps if r.get("texture_path_id","") not in ("","0")}
    world_textures = {k:v for k,v in texture_by_id.items() if k in world_texture_ids or WORLD.search(v.get("Name",""))}

    source_objects, source_errors, containers = scan_unity(source)
    output_files = file_index(existing)
    output_files.update(file_index(repo / "01_MESH_ASSETS"))
    output_files.update(file_index(repo / "recovered/asset_extraction"))

    # Existing extraction manifests are authoritative for known mesh IDs; actual local files are checked too.
    records, seen = [], set()
    def add_record(kind, pid, name, source_container="", source_class="", extra=None):
        key = (kind, str(pid), str(source_container))
        if key in seen: return
        seen.add(key)
        paths = output_files.get(str(pid), [])
        status, reason = "MISSING", "No matching extracted output file found in indexed output/repository trees."
        if paths:
            status, reason = "EXISTING/VALIDATED", "Matching output file(s) found; verify against the source bytes before final PASS."
        row = {"category":kind, "path_id":str(pid), "name":name, "source_container":source_container,
               "source_class":source_class, "status":status, "reason":reason,
               "existing_paths":";".join(paths)}
        if extra: row.update(extra)
        records.append(row)

    for pid, r in world_mesh.items():
        idx = index_by_id.get(pid, {})
        objname = "mesh_" + pid + "_" + re.sub(r"[^A-Za-z0-9_.-]+","_",r["MeshName"]) + ".obj"
        geom = geom_by_name.get(objname, {})
        status = "EXISTING/VALIDATED" if idx.get("Status","").startswith("PASS_") and geom.get("Status") == "PASS" else "FAILED/UNRESOLVED"
        paths = output_files.get(pid, [])
        # Existing OBJ/raw binary evidence is separately reported; manifest validation alone does not prove local bytes exist.
        records.append({"category":"Mesh","path_id":pid,"name":r["MeshName"],"source_container":"see source object scan",
                        "source_class":"Mesh/ClassID 43","status":status,
                        "reason":f"Index={idx.get('Status','NO_RECORD')}; geometry={geom.get('Status','NO_RECORD')}; local/repo matches={len(paths)}",
                        "existing_paths":";".join(paths),"byte_size":r.get("ByteSize",""),"data_offset":r.get("DataOffset",""),
                        "material_ids":";".join(sorted({x.get('material_path_id','') for x in assign_by_mesh.get(pid,[])}))})
    for pid, r in world_textures.items():
        add_record("Texture2D", pid, r.get("Name",""), r.get("StreamPath",""), "Texture2D/ClassID 28",
                   {"width":r.get("Width",""),"height":r.get("Height",""),"format":r.get("FormatName",""),
                    "data_source":r.get("DataSource",""),"stream_offset":r.get("Offset",""),"stream_size":r.get("Size","")})
    for o in source_objects:
        if WORLD.search(o.get("name","")) or (o.get("object_type","") in ("Mesh","Texture2D") and
            ((o.get("object_type")=="Mesh" and o.get("path_id") in world_mesh) or
             (o.get("object_type")=="Texture2D" and o.get("path_id") in world_textures))):
            add_record(o.get("object_type","UnityObject"), o.get("path_id",""), o.get("name",""),
                       o.get("source_container",""), str(o.get("class_id","")),
                       {"source_read_error":o.get("read_error",""),"source_byte_size":o.get("byte_size","")})
    for e in source_errors:
        records.append({"category":"SourceScanError","path_id":e.get("path_id",""),"name":"",
                        "source_container":e.get("source_container",""),"source_class":"",
                        "status":"FAILED/UNRESOLVED","reason":e.get("error",""),
                        "existing_paths":""})

    # Duplicate path IDs across multiple source containers are explicitly flagged.
    counts = Counter((r.get("category"),r.get("path_id")) for r in records if r.get("path_id"))
    for r in records:
        if counts[(r.get("category"),r.get("path_id"))] > 1:
            r["status"] = "DUPLICATE"
            r["reason"] = (r.get("reason","") + " Duplicate category/PathID appears in multiple source records.").strip()

    fields = sorted({k for r in records for k in r})
    with (report_dir/"world_asset_audit.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(records)
    with (report_dir/"world_asset_audit.json").open("w",encoding="utf-8") as f:
        json.dump({"scope":"WORLD ONLY","source":str(source),"repo":str(repo),"existing_output":str(existing) if existing else None,
                   "containers":[str(x) for x in containers],"summary":dict(Counter(r["status"] for r in records)),
                   "world_mesh_manifest_count":len(world_mesh),"world_material_assignment_rows":sum(map(len,assign_by_mesh.values())),
                   "world_material_count":len(world_materials),"matched_world_texture_links":len(world_texmaps),
                   "world_texture_count":len(world_textures),"source_object_count":len(source_objects),
                   "source_scan_errors":source_errors,"records":records},f,indent=2)
    summary=Counter(r["status"] for r in records)
    with (report_dir/"WORLD_AUDIT_SUMMARY.txt").open("w",encoding="utf-8") as f:
        f.write("WORLD ONLY — DISCOVERY / EXTRACTION GAP AUDIT\n")
        f.write(f"Source: {source}\nRepository: {repo}\nExisting output: {existing or 'NOT FOUND'}\n")
        f.write(f"Unity containers scanned: {len(containers)}\nSource objects enumerated: {len(source_objects)}\n")
        f.write(f"World mesh IDs from manifest: {len(world_mesh)}\n")
        f.write(f"World mesh-material assignment rows: {sum(map(len,assign_by_mesh.values()))}\n")
        f.write(f"World materials: {len(world_materials)}\nMatched texture links: {len(world_texmaps)}\n")
        f.write(f"World Texture2D IDs: {len(world_textures)}\n")
        f.write("Statuses:\n")
        for k in ("EXISTING/VALIDATED","MISSING","DUPLICATE","FAILED/UNRESOLVED"):
            f.write(f"  {k}: {summary.get(k,0)}\n")
        f.write(f"Source scan errors: {len(source_errors)}\n")
        f.write("\nNo extraction was performed. Existing outputs and source data were not modified.\n")
    print("WORLD AUDIT COMPLETE")
    print("CSV:", report_dir/"world_asset_audit.csv")
    print("JSON:", report_dir/"world_asset_audit.json")
    print("SUMMARY:", report_dir/"WORLD_AUDIT_SUMMARY.txt")
    print("STATUS:", dict(summary))
    print("EXTRACTION: NOT RUN")

if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print("WORLD AUDIT FAILED:", repr(exc), file=sys.stderr)
        sys.exit(2)
