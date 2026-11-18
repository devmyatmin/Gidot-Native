# Gidot-Native

# LAST UPDATE PLAN — FRESH EXTRACTION FOR GODOT

## 1. GITHUB IS REFERENCE ONLY

Repository: https://github.com/devmyatmin/Gidot-Native.git

Inspect the repository in **READ-ONLY mode** only to retrieve reference information needed to make the extraction script:

- Asset IDs / PathIDs
- Original asset names and file names
- Asset types and formats
- Folder and file naming conventions
- Object relationships, mappings, and metadata
- Required extraction targets and reference details

**Do not use GitHub files as extraction inputs or as replacement assets. Do not reuse old extracted assets from GitHub. Do not restart extraction from GitHub.**

## 2. KEEP ONLY GODOT-VERIFIED PASS RESULTS

The only existing outputs that may be retained are items explicitly verified as **PASS for the current Godot project**.

- Identify those Godot PASS items and record their exact IDs and paths.
- Exclude those verified PASS items from the new extraction workload.
- Do not assume that an old extraction result is a Godot PASS.
- Do not preserve or reuse other old extraction outputs just because they exist.

## 3. FRESH-EXTRACT EVERYTHING ELSE

Every required item that is not explicitly verified as PASS for the current Godot project must be extracted again from the original local game data.

- Extraction source: the user's Android local folder `Documents/Stranded Deep`.
- Do not use old OBJ, PNG, BIN, converted assets, or previous extraction outputs as source material.
- Do not use old extraction scripts or old extraction results as asset inputs.
- Use GitHub reference IDs, names, formats, and mappings only to identify and locate the correct original objects.
- Write all new extraction outputs to a clean, dedicated Godot output directory.
- Never overwrite or alter the original game data or the GitHub repository during extraction.

## 4. TERMUX SCRIPT REQUIREMENTS

Write a new script based on the verified GitHub reference information and the current Godot PASS inventory.

The script must:

1. Read GitHub-derived reference metadata locally; it must not download GitHub assets as extraction inputs.
2. Build an explicit exclusion list containing only current Godot PASS items.
3. Select all other required assets for fresh extraction from the original local game data.
4. Support the required asset types and their actual formats.
5. Validate each newly extracted output against its source object and expected metadata.
6. Produce clear PASS / FAIL / MISSING reports, including IDs, names, formats, source locations, output paths, and validation details.
7. Never classify an item as PASS when validation is incomplete or any check fails.

## 5. REQUIRED WORKFLOW

**READ-ONLY GITHUB REFERENCE INSPECTION**
→ **IDENTIFY CURRENT GODOT PASS ITEMS**
→ **EXCLUDE ONLY THOSE PASS ITEMS**
→ **FRESH-EXTRACT ALL OTHER REQUIRED ITEMS FROM LOCAL ORIGINAL DATA**
→ **STRICT VALIDATION AND REPORTING**


## 6. MANDATORY REPOSITORY REFERENCE AUDIT — OBJECT METADATA ONLY

**IMPORTANT — READ THIS BEFORE WRITING OR RUNNING ANY EXTRACTION SCRIPT.**

**THE GITHUB REPOSITORY IS THE REFERENCE CATALOG. INSPECT ITS EXISTING FILES, CODE, REPORTS, MANIFESTS, TABLES, AND DOCUMENTATION FOR OBJECT IDENTIFIERS AND METADATA. DO NOT GUESS IDENTIFIERS. DO NOT IGNORE EXISTING REFERENCE DATA. DO NOT RE-EXTRACT ITEMS THAT ARE ALREADY VERIFIED AS CURRENT GODOT PASS.**

For every required object, collect and preserve all available reference fields before writing the local extraction script:

- Original object name and any alternate/name fields.
- Source container / original asset filename.
- PathID and any other asset/object ID; always record the container alongside the ID because PathIDs are not globally unique.
- Unity ClassID, serialized object type, and asset format.
- Object category: GameObject, Transform, Mesh, Texture2D, Material, Shader, Font, Sprite, Audio, Animation, Prefab, or other actual type found in the repository.
- Mesh/model identifiers and linked renderer, material, and texture references.
- Texture identifiers, dimensions, format, mipmap data, and linked material references when recorded.
- Material and Shader names/IDs and their texture/property references when recorded.
- Font name/family, Font or TMP font asset name/ID, source font file/extension, atlas/texture ID, material ID, and any character/glyph metadata available in the repository.
- Object relationships and dependency/reference mappings.
- Existing extraction state, exact output path, validation evidence, and whether it is explicitly verified as PASS for the current Godot project.

Create a traceable reference record for each object. Keep unknown fields explicitly marked UNKNOWN; never invent a name, ID, font, relationship, output path, or validation result. Where references conflict, record the conflict and resolve it against the original local source before extraction.

**SCRIPT RULE:** The new Termux script must consume the verified reference catalog (names, container + PathID, ClassID/type, font/model/texture/material IDs, relationships, and current-Godot PASS exclusions). It must extract only from the original local `Documents/Stranded Deep` data. GitHub is never an extraction source.

**NO SHORTCUTS:** Do not focus on one subsystem (for example Ceto) while ignoring the rest of the required object catalog. Do not write a selective extraction script until the repository reference inventory and current-Godot PASS inventory have been checked.

## NON-NEGOTIABLE RULE

**GitHub is for reference information only. The original local `Documents/Stranded Deep` game data is the extraction source. Only items already verified as PASS for the current Godot project are exempt. Everything else required must be freshly extracted.**

Do not reuse other old extraction outputs. Do not treat old extraction success as Godot PASS. Do not restart extraction from GitHub.
