# Qartographer QQBSP Linux baseline

This is an independent development compiler, not a production replacement.
`qqbsp` is the primary downstream executable; upstream's `qbsp` target remains.
Both link the same corrected `libqbsp`. A downstream-built `qbsp` is therefore
**not** the pristine comparison compiler. No compiler is installed by these steps.
MAP syntax, hull dimensions, tolerances and BSP serialization are unchanged.

## Source and patch ownership

Branch: `qartographer/qqbsp-alpha10`. Upstream baseline:
`ccaeb8457a1267860ebe99ed1df7394ebdd6b435` (peeled `2.0.0-alpha10`;
annotated tag `c00577f00a216b53c6667e6e0b8f16083967de94`). The fork initially
had only main at `36eec1da2a194467e6baac2f444c2dd04b57d266`, also the inspected
upstream main. We deliberately start at the experimentally tested alpha10;
main includes later behavioral changes, notably INSIDE -> AUTO default fill.
`origin` is WarrenMarshall/ericw-tools; `upstream` is ericwa/ericw-tools.
Neither remote has been pushed by this bootstrap.

`baseline.json` pins three gitlinks, configure-time inputs and fixture hashes.
P1 commit `7f2ef6f3` changes only CreateBrushWindings' clip_front keepon argument
and explains why: two near-coincident supporting faces can both classify wholly
ON and disappear, depriving BSP construction of their boundary. Retain them
without changing epsilon or welding planes. `P1.patch` is the original evidence
patch, not an extra patch to apply on this branch. `P2-unapplied.patch` preserves
the merged `_hulls` routing candidate and is explicitly excluded.

Provenance: Qartographer's docs/qbsp_fork_feasibility.md and evidence directory,
at the editor revision recorded in baseline.json. Copied independent Python
halfspace/BSP oracles and frozen MAP fixtures originate there. full_oracle.py
retains the existing source-support, source-clearance and hull-0 comparison
checks; only failure/count serialization was added. No authored MAP was edited.
The Halloween full-on MAP hash is
`16250e50546f9d1c4654d75e0a6683f70f7eff332ec730793c5f836d39716318`.
This agrees with the preserved file, full-map.json, textured-compiles.json and
export-equivalence.json. The older provenance.json instead records `91593e…`;
that inconsistent field is not treated as fixture authority or silently copied.
The fixtures include generated Halloween geometry and texture names, no WADs or
mod assets; do not treat them as a distributable gameplay package.

## Build

Reference host: Ubuntu 24.04 x86_64, GCC 13.3.0, GNU ld 2.42,
CMake 3.28.3, Ninja 1.11.1, Python 3.12.3. Install those tools before running.
Use a clean Git checkout with recursive submodules. Keep the workspace outside
the source tree. Network provisioning downloads checksum-verified TBB 2021.11.0,
Embree 4.4.0 and nlohmann JSON 3.12.0 archives. Googletest is checked out at its
full revision. URLs and SHA-256 values live in baseline.json. Existing archive
copies may be placed at WORK/deps/{tbb,embree,json}.archive, and a pristine
Googletest checkout at WORK/deps/googletest, for offline use. Downloads are not
vendored. Top-level CMake requires Embree and Googletest even though the QBSP
runtime does not link Embree. Do not run the upstream package/install scripts.

```sh
git checkout qartographer/qqbsp-alpha10
git submodule update --init --recursive
python3 qartographer/build.py --work /tmp/qqbsp-work --pristine
python3 qartographer/build.py --work /tmp/qqbsp-work
/tmp/qqbsp-work/patched-build/qbsp/qqbsp -help
python3 qartographer/regress.py \
  /tmp/qqbsp-work/pristine-build/qbsp/qbsp \
  /tmp/qqbsp-work/patched-build/qbsp/qqbsp /tmp/qqbsp-results --full
```

The recipe uses identical RelWithDebInfo, C++20 and compiler configuration for
both builds, with only the correction/frontend identity differing. It configures
on each invocation so identity reflects HEAD. Existing upstream version reporting
prints on startup/help; qqbsp adds `Qartographer qqbsp`, full upstream/downstream
SHAs, dirty marker and `patches=P1`. There is no invented --version interface.
The Linux alpha10 help path returns zero. Reconfigure after changing HEAD or
tracked sources; the identity is a configure-time snapshot, not a live Git query.
Windows inherits the qqbsp.exe target but is untested and unpackaged.

build.py emits manifests recording toolchain, source status, exact configure
arguments, binary/runtime hashes and ldd output. Keep the adjacent TBB shared
libraries with the binary; the existing $ORIGIN RPATH finds them. System glibc,
libstdc++ and other runtime requirements remain host-specific. This recipe pins
inputs and checks tool versions; it is not a container/sysroot portability promise
or a bit-for-bit reproducibility claim. No two-clean-build binary comparison has
been performed. Corresponding source and dependency license obligations must be
handled before redistribution; retain upstream COPYING and notices.

## Regression contract

The default regression run compiles the four-brush reduced failure and the
frozen 33-brush RollerSpline with default flags and -chopfragment. --full also
compiles two unchanged preserved Halloween exports. All use -bsp2 -notex
-nopercent; reduced/full additionally use -chopfragment. Stock and patched use
identical flags per case. MAP copies and compiled outputs stay in a new output
directory. The runner checks the fixture lock before compiling and asserts stock
failure and downstream success, including both actor hulls and unchanged hull-0
samples. Compile errors and missing result files fail the run. The underlying
research helpers are not themselves all assertive; use regress.py as the gate.

Use reduced/Roller for focused changes. Run --full for P1-path changes, baseline
upgrades and release candidates. Record new input hashes explicitly when accepting
new fixtures. Never update expected results merely to hide a regression. See
BOOTSTRAP.md for measured bootstrap results and remaining acceptance work.

## Synchronizing upstream

Keep origin/main as the upstream mirror and the downstream branch separate.
Fetch upstream and inspect the exact candidate SHA and its changes first. Create
an update branch from the known-good downstream commit; merge the chosen upstream
SHA there (never reset the downstream branch to upstream). Review submodule,
FetchContent, compiler flag, version/fill and output changes explicitly. Update
baseline.json and the upstream identity string together only after choosing the
new baseline. The pristine builder archives that new baseline, not the downstream
working tree. Its fixtures/oracles remain independently pinned.

Before merging, inspect whether upstream already includes P1, using its code and
regression behavior, not just a commit subject. The original downstream commit
already exists in history: do not reapply P1.patch or cherry-pick it again. Resolve
an upstream equivalent as one implementation. If upstream supersedes P1, retire
the downstream patch entry and update the hardcoded patches=P1 banner/assertion;
keep the regression. Never keep competing implementations. An upstream fix may
make the pristine-negative expectation obsolete: review and change that gate to
require both to pass rather than intentionally resurrecting the bug.

Build pristine candidate and downstream with the same recipe/environment, run
--full and relevant upstream QBSP tests, inspect intentional output differences,
and complete the native/contents gates before promoting the branch. Preserve the
old source commit, binaries, runtime libraries, manifest and evidence for rollback.
P2 is a separate feature decision and must never ride along in an upstream sync.
Push/publish or install only when explicitly requested.

## Local validated deployment

The normal local command builds, runs the full regression gate, deploys, and
verifies startup/hash/identity. A failed command exits nonzero and is not an
accepted deployment. The build-only command above never deploys experiments.

```sh
python3 qartographer/validated_build.py --work /tmp/qqbsp-work \
  --results /tmp/qqbsp-results-new
# Independently deploy a previously validated artifact:
python3 qartographer/deploy.py --work /tmp/qqbsp-work \
  --results /tmp/qqbsp-results-new
```

Default destination:
`/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp`.
Override with --destination /another/directory/qqbsp or QQBSP_DEPLOY_PATH. The
parent must exist. Only a destination named qqbsp is accepted. The deploy command
requires a clean committed build manifest, a full PASS receipt and matching
compiler hash, stages the file in that directory, preserves its executable mode,
checks its hash and executes its help/version path there before atomic rename.
It verifies the final path again and writes deployment.json in the work directory.

No existing runtime libraries or other utilities are overwritten. Destination
TBB libraries must already satisfy the built executable; staged startup uses
$ORIGIN and clears LD_LIBRARY_PATH/LD_PRELOAD to avoid accidentally relying on
the build environment. Missing/incompatible libraries cause explicit failure
before replacement. The current local compiler directory supplies TBB .so.12 and
TBB malloc .so.2. This startup check establishes local loader compatibility; it is
not a portable Linux package or a full compile under every destination runtime.
