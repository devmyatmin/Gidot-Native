# Gidot-Native

# 🚨 WORLD ONLY — LAST UPDATE PLAN 🚨

## WORLD ASSET WORKFLOW — FOLLOW THIS ORDER EXACTLY

**SCOPE: WORLD ASSETS ONLY. DO NOT EXPAND THIS TASK TO OTHER GAME SYSTEMS.**

### 1. GITHUB — READ-ONLY INSPECTION

Use `https://github.com/devmyatmin/Gidot-Native` as the existing-work reference.

- Inspect the existing folders, files, reports, asset inventories, IDs, PathIDs, extraction results, and rewritten C# logic where relevant to World.
- Identify what already exists and what is still missing.
- Trace World-related Mesh, Texture, Material, and other resource references from the available reports and source metadata.
- Record exact source file/container, object type, name, ID/PathID, dependencies, and existing output location.
- Do not assume an ID is a Mesh PathID when it belongs to a Texture or another object type.
- Do not restart, overwrite, delete, or duplicate existing work.
- Do not extract game assets from GitHub. GitHub is the inspection/reference source, not the original asset source.

### 2. ORIGINAL STRANDED DEEP GAME DATA — ASSET SOURCE

Use the original local game data as the source for any required World asset extraction:

`/storage/emulated/0/Documents/Stranded Deep/Stranded_Deep_Data/`

- Read the original game data without modifying it.
- Extract only World assets proven to be missing after the GitHub inventory audit.
- Preserve original object IDs/PathIDs and dependency relationships.
- Do not re-extract assets that are already present and validated.

### 3. TERMUX — WORLD DISCOVERY, AUDIT, AND EXTRACTION SCRIPTS

**FIRST SCRIPT: WORLD ASSET DISCOVERY + EXTRACTION GAP AUDIT**

The first script must audit before it extracts anything.

It must:
- Inventory World-related objects and their exact IDs/PathIDs across the relevant original data containers.
- Resolve and report Mesh–Material–Texture references where the available metadata permits.
- Compare discovered source objects against existing extracted outputs and GitHub reports.
- Classify every item as EXISTING/VALIDATED, MISSING, DUPLICATE, or FAILED/UNRESOLVED.
- Produce machine-readable JSON/CSV reports plus a readable summary.
- Never silently skip an object; every discovered item must receive an explicit status and reason.
- Keep source data and existing outputs unchanged during the audit.

**ONLY AFTER THE AUDIT RESULTS ARE REVIEWED:** write the separate World extraction script for confirmed missing assets. Do not guess IDs or write an extraction script from an incomplete inventory.

### 4. STRICT VALIDATION — PASS / FAIL

- PASS only when the required extraction and validation checks complete successfully with no unresolved verification error.
- Any missing dependency, byte mismatch, unsupported object, export error, or incomplete verification is FAIL.
- Report the exact object ID/PathID, source container, output path, and failure reason.
- Never count skipped, unverified, or partially processed objects as PASS.

### 5. GODOT PROJECT — FINAL WORLD INTEGRATION

After World assets are extracted and validated, prepare them for integration into the existing Godot project. Preserve the existing project and rewritten C# logic. Do not begin unrelated systems or claim the World integration is complete before it is verified.

---

## NON-NEGOTIABLE RULES

1. **WORLD ONLY.**
2. **INSPECT FIRST — SCRIPT SECOND — EXTRACT THIRD — INTEGRATE LAST.**
3. **GITHUB IS FOR READ-ONLY INSPECTION, EXCEPT THIS EXPLICITLY REQUESTED README PLAN UPDATE.**
4. **ORIGINAL GAME DATA IS THE SOURCE FOR ASSET EXTRACTION.**
5. **NO DUPLICATE EXTRACTION. NO DELETING. NO RESTARTING EXISTING WORK.**
6. **NO GUESSED IDs, NO UNVERIFIED CLAIMS, AND NO SILENT SKIPS.**
7. **REPORT REAL PASS/FAIL RESULTS ONLY.**

**CURRENT STATUS: WORKFLOW RECORDED. WORLD INVENTORY AUDIT MUST BE COMPLETED BEFORE THE WORLD EXTRACTION SCRIPT IS WRITTEN.**
