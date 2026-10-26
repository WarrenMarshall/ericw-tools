# QQBSP deployment stripping — 2026-10-26

Deployed a separately validated **debug-stripped** QQBSP while retaining the full
RelWithDebInfo development executable and hash-versioned debug archives. No compiler
algorithm, optimization setting, upstream baseline, stock utility or runtime library
was changed. Deployment is still atomic and rollback-protected.

## Sizes and cause

All sizes are file bytes (MB below means decimal MB).

| Artifact | Bytes | MB |
| --- | ---: | ---: |
| Previously deployed/original development executable | 47,766,536 | 47.77 |
| Newly validated development executable | 47,766,272 | 47.77 |
| New deployed executable, `strip --strip-debug` | 2,177,344 | 2.18 |
| Installed stock `qbsp`, untouched | 1,881,624 | 1.88 |

The validated pair shrank by **45,588,928 bytes / 95.4417%**. The original binary's
45,587,289 bytes of DWARF explain essentially all of the original gap; stripping
that original copy also produced 2,177,344 bytes. The rebuilt development file has
45,587,025 DWARF bytes; another 1,903 bytes removed are ELF/debug bookkeeping.
This was measured from section tables and separate copies, not inferred from the
RelWithDebInfo label. The original full-debug executable is also preserved.

Development remains GCC 13.3.0, CMake RelWithDebInfo **`-O2 -g -DNDEBUG`**, with the
existing LTO configuration unchanged. The new downstream identity reflects the
packaging-workflow commit; upstream remains
`ccaeb8457a1267860ebe99ed1df7394ebdd6b435` with P1 alone.

Stock has no DWARF but retains `.symtab`; its ELF compiler comment identifies GCC
11.4.0. Both executables dynamically require the same six libraries (TBB, TBB malloc,
libstdc++, libm, libgcc_s and libc), have $ORIGIN RUNPATH, and do not link Embree.
Actual local TBB 2021.11 libraries are byte-identical between build and installation.
The new file remains 295,720 bytes larger than stock; `.text` alone is 229,157 bytes
larger. Stock's exact optimization/LTO and static-dependency build records are not
available, so the remaining difference cannot be assigned precisely to flags or
toolchain choices. It was not addressed by changing optimization or linking.
[ELF measurements](strip_evidence/elf-investigation.json).

## Packaging and symbol retention

build.py still creates `WORK/patched-build/qbsp/qqbsp` with all DWARF and records it
in patched-manifest.json. artifacts.py copies it to `WORK/deployment/qqbsp` and runs
GNU strip 2.42 with **only `--strip-debug`**, producing deployment-artifact.json.
It does not use --strip-all, --strip-unneeded, change source files or strip libraries.

Preparation verifies no DWARF remains in the smaller copy; all allocated sections,
program headers, entry point, dynamic symbols, build ID, unwind/exception data and
all **3,507 defined diagnostic symbols** remain unchanged. The development hash
must stay unchanged. GDB still resolves `CreateBrushWindings` to source line 270 in
the development binary. [GDB evidence](strip_evidence/development-gdb.txt).

Before deployment, the full matching executable and build manifest are retained at:

```
~/dev/ericw-tools/build-symbols/a097cb6a6288b930eb018797464ef6a2a7e64d173fd113bdd1659167a1be30ff/qqbsp
```

The original prior executable is also archived under its original hash beginning
`9a36f9b4…`. These ignored, persistent directories survive later rebuilds and
/tmp workdir cleanup; keep the matching archive while its deployment is in use.
Load the archived executable explicitly in GDB for source/line debugging of a
matching process/core. No separate .debug file, automatic debug-link installation,
or compiler rebuild reproducibility claim is needed.

## Independent validation and comparison

Both actual artifacts independently passed the complete existing Tier 3 gate:

- Startup and matching version/build identity; 13 upstream QBSP tests each.
- Ordinary MAP/BSP29, duplicate/empty brushes, mixed contents and four thin/opening cases.
- Reduced collision: **0 failures**, versus 104 for pristine.
- Frozen RollerSpline: **0 failures in hulls 0/1/2**, default and -chopfragment.
- Halloween source-derived collision oracle: **0 failures**, versus 25 for pristine;
  required floor support/clearance and all 10,070 point/projectile comparisons pass.
- Installed stock VIS/LIGHT compatibility and fresh QrustyQuake native WALK/BSP29
  validation with **exitstyle 2**. Both native runs exit 0 normally in about 5.27 s;
  movement, server clocks and grounding states match exactly.

Full-on QBSP elapsed was 13.526 s development and 12.869 s stripped, sequential
single trials. This is timing noise evidence, not a stripping speedup claim;
executable loaded sections are unchanged. No unexplained performance regression
or changed collision semantics was observed.

All **17 MAP inputs match byte-for-byte**. Of **18 BSP outputs**, 13 match raw bytes.
The other five differ only in verified nonsemantic ordering, observed in the
pristine control as well:

- Three full-map outputs differ only in leaf face-list order. Each leaf's face
  multiset, including duplicate counts, matches; every other byte is identical.
  The existing `qbsp/faces.cc` builds these lists through `std::set<face_t *>`, whose
  pointer ordering can vary across processes. No compiler fix was attempted.
- The ordinary BSP29 and its native copy differ only in stock LIGHT's allocated
  lightmap order and corresponding offsets. Each face's complete lightmap chunk,
  including padding, is byte-identical. Stock LIGHT uses atomic file-space allocation.

The comparison gate records both raw hashes and the applicable normalization;
it never modifies BSP files. Every other byte, including geometry/collision,
model data, membership, face fields, pixels and unknown trailing data, must match.
Focused regressions reject changed membership/duplicates, pixels or geometry fields.
Source-derived collision oracles and tolerances were unchanged.
[Comparison receipt](strip_evidence/artifact-comparison.json),
[development Tier 3](strip_evidence/development/tier-results.json),
[deployment Tier 3](strip_evidence/deployment/tier-results.json).

Five focused unit checks passed (three packaging guards, two BSP comparison tests).
Deployment checks also reject an unavailable destination, protected stock filename,
missing TBB runtime and substitution of the development hash; injected final
verification failure restores the previous executable. [Guard results](strip_evidence/deployment-guards.json).
The already-passing Tier 3 runs were reused after correcting the comparison for the
observed ordering behavior; they were not redundantly rerun.

## Hashes and actual deployment

Development SHA-256:

```
a097cb6a6288b930eb018797464ef6a2a7e64d173fd113bdd1659167a1be30ff
```

Deployment SHA-256:

```
49d766579a03701d6a5bb3560112bc756afdb8cf4488242e0b8db72668d8c8c0
```

Installed at:
`/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp`.
The receipt records the actual stripped source artifact/hash, development hash and
debug archive. Staged and final destination startup/hash/identity passed with
loader override variables cleared. Every pre-existing stock utility and library
remains hash-identical; only qqbsp changed. Executable permissions were preserved.
[Deployment receipt](strip_evidence/deployment.json),
[destination verification](strip_evidence/destination-verification.json).

Final identity:

```
Qartographer qqbsp, upstream=ccaeb8457a1267860ebe99ed1df7394ebdd6b435, downstream=a39a599d08967998d01e85d10ac356f823e27a35, patches=P1
```

## Commands and limits

The normal command is unchanged; it now performs build/preparation, independent
Tier 3 on each artifact, comparison, then stripped deployment and verification:

```sh
SDL_VIDEODRIVER=dummy python3 qartographer/validated_build.py \
  --work /tmp/qqbsp-work --results /tmp/qqbsp-release-new
```

Standalone preparation, tier selection, comparison and deployment commands are in
[AGENTS.md](../AGENTS.md) and [README.md](README.md). Preparing an artifact does not
authorize installation. Existing single-artifact receipts cannot validate another
artifact's hash, and a stale/tampered prepared file is rejected.

This is local Linux x86_64 ELF packaging using GNU binutils, not Windows/macOS or
portable distribution packaging. Stripping does not lower ABI requirements: the
binary still needs GLIBC_2.38 and GLIBCXX_3.4.32 symbols and the existing TBB runtime.
The observed stock executable requires older symbol versions (up to GLIBC_2.34 and
GLIBCXX_3.4.29). No older-system portability, two-clean-build binary reproducibility,
automatic external debug-symbol discovery or distribution license bundle is claimed.
No production exporter, authored map or compiler algorithm changed.
