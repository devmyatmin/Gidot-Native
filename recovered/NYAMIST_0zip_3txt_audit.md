# NYAMIST / Castaway Depths — 0.zip (text.txt–text 3.txt) Static Audit

**Scope:** Read-only analysis of the four text logs contained in the latest uploaded `0.zip` (157,853 bytes). No APK, source, or device files were modified. This report reflects the command output captured in those logs, not a fresh execution against the user's Termux filesystem.

## 1. Key finding: Real3D has a real Vulkan render loop in its native code

The `text 2.txt` and `text 3.txt` logs identify these local ELF symbols in `CastawayDepths_Real3D_engine.so`:

- `renderLoop()` at virtual address `0x13d298`, size 1,460 bytes.
- `kMeshVerts` at `0x2ba8`, size 1,271,268 bytes.
- Function-pointer storage for Vulkan calls including instance/device creation, command buffers, render pass, pipeline, buffer/memory, draw, swapchain acquire and present.

The `text 3.txt` disassembly of `renderLoop()` shows indirect calls through the `gVk` function-pointer table. The addresses and symbol table offsets map these calls to the following Vulkan operations:

- `vkWaitForFences` / `vkResetFences` before frame work.
- `vkAcquireNextImageKHR` to acquire a swapchain image.
- `vkResetCommandBuffer` and `vkBeginCommandBuffer`.
- `vkCmdBeginRenderPass`.
- `vkCmdBindPipeline`.
- `vkCmdPushConstants`.
- `vkCmdDraw` with `vertexCount = 35,313`, `instanceCount = 1`, `firstVertex = 0`, `firstInstance = 0`.
- `vkCmdEndRenderPass` and `vkEndCommandBuffer`.
- `vkQueueSubmit`.
- `vkQueuePresentKHR`.

This is strong static evidence that the library contains an implemented Vulkan frame-submission path, not merely Vulkan function-name strings. It still does **not** prove that every call succeeds at runtime, that the render loop is reached on the device, or that the presented frame is visually correct.

## 2. Mesh data relationship

`kMeshVerts` is reported as 1,271,268 bytes. Dividing by the draw count:

`1,271,268 / 35,313 = 36 bytes per vertex`.

The render loop's `vkCmdDraw` call uses exactly 35,313 vertices. The matching count and exact 36-byte stride strongly suggest the static vertex payload is the geometry used by this draw. The precise vertex attribute layout (for example position/normal/UV) is **not established** by these logs and must not be guessed.

## 3. Original PC game inventory

`text 1.txt` reports the original Unity game contains:

- `UnityPlayer.dll`: 28,773,464 bytes.
- `Assembly-CSharp.dll`: 3,432,448 bytes.
- `Assembly-CSharp-firstpass.dll`: 642,048 bytes.
- `resources.assets.resS`: 1,373,682,164 bytes.
- `resources.assets`: 184,519,152 bytes.
- Multiple `sharedassets0`–`sharedassets4` `.assets`, `.resS`, and `.resource` files.

The standalone file search for `.shader`, `.mat`, `.hlsl`, `.cginc`, and related extensions returned no listed matches. This does **not** mean the game has no shaders/materials: Unity commonly serializes such objects into asset containers and bundles.

The large `.assets` and `.resS` files are promising sources for extracting original meshes, textures, materials, shader references, and other serialized Unity objects. Their contents have not yet been parsed in this audit.

## 4. ELF and dynamic-loading evidence

The logs show:

- ELF format: 64-bit little-endian AArch64.
- `dlopen` and `dlsym` are imported, consistent with loading Vulkan dynamically.
- Android native-window functions are imported: `ANativeWindow_fromSurface`, `ANativeWindow_getWidth`, `ANativeWindow_getHeight`, `ANativeWindow_release`.
- Vulkan PFN variables are local data symbols in `.bss` / writable data, and `renderLoop()` loads and calls through function pointers.
- The captured SHA-256 for the audited Real3D library is `def25443058820e2236c7a109c615c94c7a18ebab93cd214229727d209534dbb`.

## 5. Important limits / unverified points

This ZIP contains terminal transcripts, not the APK binary or the original Unity asset files themselves. Therefore this audit cannot yet verify:

1. Whether all Vulkan entry points were resolved successfully on the target device.
2. Whether `vkCreateGraphicsPipelines`, shader module creation, descriptor/resource setup and vertex-buffer upload all succeed at runtime.
3. Whether the `kMeshVerts` payload is a mesh from the original PC game or a separately generated approximation.
4. The vertex layout, index topology, material/texture mapping, shader source/SPIR-V semantics, coordinate system, and scene provenance.
5. Whether swapchain presentation is stable across resize, rotation, pause/resume, and surface recreation.
6. Whether the original PC game's assets can be reused directly without format conversion or shader/material adaptation.

## 6. Recommended next investigation order

1. **Preserve and fingerprint:** record SHA-256 for all three APKs, all extracted engine `.so` files, and the original Unity asset files. Do not overwrite the working APKs.
2. **Trace the complete native initialization path:** inspect the functions that resolve Vulkan PFNs and create instance/device/surface/swapchain, buffers, shader modules, render pass, pipeline, framebuffers, semaphores and fences.
3. **Decode `kMeshVerts`:** inspect the first several vertex records as floats/hex, establish the 36-byte attribute layout, and check bounds/finite values. Do not assume attribute semantics until corroborated.
4. **Parse Unity assets read-only:** enumerate serialized object types and names in `resources.assets`, `sharedassets*.assets`, and corresponding `.resS` / `.resource` files; identify Mesh, Texture2D, Material, Shader, ShaderVariantCollection and AssetBundle records.
5. **Compare geometry:** compare extracted original mesh vertex/index counts, bounds and data against the APK's `kMeshVerts` payload.
6. **Runtime verification:** use Android logcat/Vulkan validation or explicit per-call result logging to prove successful execution and presentation; then capture a frame and verify orientation, geometry, textures and materials.

## 7. Files included in the uploaded ZIP

- `text.txt`: earlier APK build and Termux backup inventory transcript.
- `text 1.txt`: original Unity game file inventory and Real3D ELF/strings audit.
- `text 2.txt`: Real3D local symbol table, dynamic symbols, relocations and Vulkan string offsets.
- `text 3.txt`: AArch64 disassembly of `renderLoop()` and mesh symbol/section information.

**Conclusion:** Real3D's native library contains a genuine Vulkan draw-and-present code path and a 35,313-vertex static payload with a 36-byte-per-vertex size relationship. The most valuable next step is to compare that payload against meshes extracted from the original Unity asset containers, while independently verifying runtime Vulkan success.
