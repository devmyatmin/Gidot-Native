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


## 7. SEPARATE CLEAN PROJECT — ORIGINAL FULL 3D OCEAN WORLD ONLY

**MANDATORY: CREATE A NEW, CLEAN, SEPARATE PROJECT FOR THE OCEAN WORLD. DO NOT MIX IT WITH THE EXISTING GODOT PROJECT OR ITS WORKSPACE.**

### SCOPE

Build only the original Stranded Deep-style full 3D ocean/water world. This is a realistic 3D environment target, NOT a 2D scene, NOT a cartoon, NOT a flat blue plane, and NOT a simplified mobile-game water effect.

The target is the original game's ocean presentation and environment system, using verified original-game references and local source assets wherever available. Preserve the original visual character and spatial scale as closely as the source data permits.

### REQUIRED OCEAN-WORLD CONTENT

Inspect the repository and original local game data for all relevant ocean-world components and their dependencies, including where present:

- 3D ocean surface geometry, meshes, projected-grid or equivalent surface systems.
- Multi-scale wave forms, wave displacement, normals, and surface detail.
- Water material, shaders, shader parameters, and render settings.
- Realistic lighting, sun response, specular highlights, reflections, and refraction where supported.
- Depth-based color, transparency, fog, and underwater visibility.
- Underwater environment rendering, caustics/attenuation or other effects only where supported by original references.
- Ocean horizon, sky/environment integration, and large-world visual continuity.
- Shoreline/depth interaction and ocean-to-island visual transitions where supported by original assets and references.
- Required textures, lookup textures, masks, meshes, materials, and other source dependencies.

Do not invent original IDs or pretend unsupported effects exist. Use the repository's verified names, IDs, PathIDs, ClassIDs, formats, and relationships as references; resolve missing or conflicting metadata against the original local game data.

### EXPLICITLY OUT OF SCOPE FOR THIS PHASE

**DO NOT ADD GAMEPLAY OR GAME LOGIC YET.**

Do not implement player controls, swimming, diving gameplay, buoyancy gameplay, boats, survival systems, inventory, missions, AI, damage, or other gameplay logic. Do not begin general game-system porting in this separate project. Ocean rendering/environment components and the minimum technical scene setup needed to display and validate the ocean are allowed; gameplay behavior is not.

### SOURCE AND PROJECT ISOLATION

- Keep this as a new, clean project with its own dedicated folder, scripts, assets, shaders, scenes, and reports.
- Do not modify or contaminate the existing project/workspace.
- GitHub remains READ-ONLY REFERENCE for names, IDs, metadata, dependencies, and prior verification records; it is not an asset extraction source.
- Extract required original assets only from the user's local original `Documents/Stranded Deep` game data.
- Do not use old extracted assets as source inputs.
- Do not alter original game files or the GitHub repository during local extraction/build steps.

### ACCEPTANCE CRITERIA

The phase is complete only when the separate project can display and validate a coherent, continuous, full 3D ocean world with the original-style water surface and the supported visual/environment effects listed above. It must not be represented as complete if it is only a flat plane, a 2D/cartoon effect, a static screenshot, or a collection of unconnected assets.

Produce explicit PASS / FAIL / MISSING reports for required ocean components and their source references. Mark unsupported or unavailable original features as MISSING rather than fabricating them.

**PHASE BOUNDARY: FULL 3D OCEAN WORLD FIRST. NO GAMEPLAY OR GENERAL GAME LOGIC UNTIL THIS OCEAN-ONLY PROJECT PHASE IS ACCEPTED.**

## NON-NEGOTIABLE RULE

**GitHub is for reference information only. The original local `Documents/Stranded Deep` game data is the extraction source. Only items already verified as PASS for the current Godot project are exempt. Everything else required must be freshly extracted.**

Do not reuse other old extraction outputs. Do not treat old extraction success as Godot PASS. Do not restart extraction from GitHub.
