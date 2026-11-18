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

## NON-NEGOTIABLE RULE

**GitHub is for reference information only. The original local `Documents/Stranded Deep` game data is the extraction source. Only items already verified as PASS for the current Godot project are exempt. Everything else required must be freshly extracted.**

Do not reuse other old extraction outputs. Do not treat old extraction success as Godot PASS. Do not restart extraction from GitHub.
