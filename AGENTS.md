# QQBSP agent instructions

## Scope

This fork exists exclusively for QQBSP, Qartographer's customized EricW QBSP.
In scope: QBSP geometry/collision correctness, shared code directly required by
QBSP, minimal CMake changes, QBSP regressions/benchmarks/diagnostics, identity,
provenance and deployment. Shared-source changes require a demonstrated QBSP
requirement, narrow scope and independent testing proportional to dependencies.

Do not modify VIS/LIGHT source, tests, algorithms, performance or build behavior.
Light preview, texture utilities, other EricW applications, general modernization,
unrelated upstream bugs, speculative optimization, shared-library rewrites and
customized complete toolchain builds/distribution are out of scope. Stock VIS,
LIGHT and other utilities remain authoritative. They may consume test BSPs for
compatibility checks. Build only qqbsp, its dependencies, qqbsp_tests and pristine
qbsp for comparison. Never run package/all targets or unrelated application suites.

Success: identifiable, validated qqbsp accepting standard Quake MAP and emitting
standard Quake BSP, with the smallest maintained set of demonstrated corrections.
Keep upstream's qbsp target and share compiler code; a downstream-built qbsp also
contains our patches and is not the pristine control. Never overwrite stock qbsp.
No new BSP formats, engine requirements, speculative collision repairs, production
exporter integration or threaded architecture without explicit assignment scope.

## Baseline and maintenance

Read qartographer/README.md, baseline.json and BOOTSTRAP.md. The original
investigation is ../qartographer/docs/qbsp_fork_feasibility.md. P1 is accepted;
P2-unapplied.patch is a separate candidate and must stay unapplied. Each compiler
correction needs an isolated commit, explanation and failing-before/passing-after
regression. Separate build/workflow changes. Preserve upstream licenses/notices.
Do not spawn agents by default.

Follow README.md's upstream merge/retirement procedure: inspect and pin the
candidate upstream SHA; do not reset downstream history, reapply existing patches,
or keep duplicate implementations. Review fill defaults, dependency changes and
intentional BSP differences. Retire patches only after tested upstream equivalents.

## Commands and testing tiers

Run from the repository root. Reference Linux tools and dependency provisioning
are in README.md. --work holds downloads, builds and manifests; --results must be
a new disposable directory. Nothing writes authored maps or installed game assets.

```sh
# First checkout: pin the submodules; build pristine only once per baseline.
git submodule update --init --recursive
python3 qartographer/build.py --work /tmp/qqbsp-work --pristine
# Build symbol-rich qqbsp, QBSP-only tests and a separate debug-stripped copy.
python3 qartographer/build.py --work /tmp/qqbsp-work
# Tier 1: relevant changes, frequent development checks.
python3 qartographer/tiers.py --tier 1 --work /tmp/qqbsp-work --results /tmp/qqbsp-tier1-new
# Tier 2: before accepting a compiler change; includes applicable Tier 1 checks.
python3 qartographer/tiers.py --tier 2 --work /tmp/qqbsp-work --results /tmp/qqbsp-tier2-new
# Tier 3: independently validate both artifacts, then compare exact outputs.
python3 qartographer/tiers.py --tier 3 --artifact development --work /tmp/qqbsp-work --results /tmp/qqbsp-release-new/development
python3 qartographer/tiers.py --tier 3 --artifact deployment --work /tmp/qqbsp-work --results /tmp/qqbsp-release-new/deployment
python3 qartographer/artifacts.py compare --work /tmp/qqbsp-work --results /tmp/qqbsp-release-new
# Independently deploy only from both matching Tier 3 receipts and comparison PASS.
python3 qartographer/deploy.py --work /tmp/qqbsp-work --results /tmp/qqbsp-release-new
# Normal local workflow: Build -> Validate (Tier 3) -> Deploy -> Verify.
python3 qartographer/validated_build.py --work /tmp/qqbsp-work --results /tmp/qqbsp-release-new
```

Tier 1 compiles successfully, checks startup/build identity, the reduced coplanar
regression, ordinary sealed MAPs, duplicate planes and empty-brush handling. Add
focused tests for the changed behavior when these do not exercise it.

Tier 2 adds frozen RollerSpline default/chopfragment, hulls 0/1/2, coplanar and
near-coplanar supports, thin recovered cells, intentional openings, shared brush
boundaries, mixed contents, degenerate handling, full Halloween collision oracle,
and the relevant upstream QBSP filter. qqbsp_tests reuses unchanged upstream QBSP
tests without linking LIGHT/VIS. Tests write into copied build-directory fixtures.
Expand the selected cases when a change creates a materially different risk.

Tier 3 requires all applicable earlier checks, full-map compilation and review of
BSP structure/collision/performance. It freshly replays matched ordinary native
WALK movement on RollerSpline, tests BSP29 with installed stock VIS/LIGHT and
loads that ordinary result in Quake. --engine, --id1 and --utilities configure
local consumers/assets. Default paths are in tiers.py. No assets are redistributed.
Native player evidence does not replace independent hull-2 checks or establish
full-map gameplay/lighting acceptance. Add relevant native cases for changed risks.

## Evidence and acceptance

Fixtures and independent MAP/configuration-space/BSP oracles live under
qartographer/fixtures and qartographer/*oracle.py, direct_probe.py and
wildspline_bsp_collision_compile.py. baseline.json pins hashes. regress.py wraps
research JSON reports with nonzero pass/fail assertions; never infer PASS merely
from a research driver's exit code. tiers.py is the acceptance entry point.

Keep reduced regressions for confirmed defects and representative historical
fixtures. Independently derived geometry expectations remain separate from BSP
outputs. Include hulls 0/1/2 where relevant. Pristine and patched BSPs may differ
for intentional corrections; hashes identify artifacts, not correctness. Separate
correctness from intentional collision-envelope semantics. Never weaken tolerances,
remove failing samples or bless a changed output merely to make tests pass.

Failed runs retain logs, XML, MAP copies, BSPs and JSON in --results; inspect those
before rerunning. Missing assets/display/dependencies and compiler execution errors
are infrastructure failures, not valid geometry evidence. Tier receipts remain
INCOMPLETE on failure; never deploy them. A passing result remains useful until
relevant code/dependencies/binary change. Stop testing when material questions are
answered. Do not run exhaustive suites for documentation or workflow-only edits.

Record source/patch/dependency identities, binary/runtime hashes and results.
Inspect timings against pristine and historical evidence; noisy differences are
not correctness failures. A >25% full compile increase requires investigation and
an explanatory --performance-note, not automatic baseline promotion. Change fixture
or performance baselines only with reviewed reasons and preserved prior evidence;
if upstream fixes P1, explicitly retire the stock-negative expectation. Do not claim
bit-for-bit reproducibility without two independently verified clean builds.

## Deployment

Development stays RelWithDebInfo at WORK/patched-build/qbsp/qqbsp, recorded by
patched-manifest.json. build.py also copies and runs GNU `strip --strip-debug` on
WORK/deployment/qqbsp, recorded separately by deployment-artifact.json. Never strip
the development file, use --strip-all, alter optimization, or strip runtime libraries.
Preparation asserts unchanged allocated sections, program headers, build ID, dynamic
symbols/unwind data and defined diagnostic symbols. Independently prepare an existing
build with `python3 qartographer/artifacts.py prepare --work /tmp/qqbsp-work`.
Run `python3 qartographer/test_artifacts.py` for focused packaging guards.

Deployment requires a clean committed build, separate development/deployment Tier 3
PASS receipts and artifact-comparison.json. MAP bytes, native states and identity must match across the two executables. BSP
comparison preserves every byte except observed pointer-ordered leaf face lists and
stock LIGHT allocation order: each leaf face multiset and each face lightmap chunk
(including padding) must still match exactly. Changed geometry, collision, membership
or pixels fail; no oracle sample or tolerance is relaxed. Both raw hashes and any
normalization are recorded in the comparison receipt. Tier/native --artifact defaults to development;
select deployment explicitly when validating the stripped copy. Receipt hashes must
identify the actual selected artifact, never substitute its development hash.
Before replacing qqbsp, deployment archives the full matching debug executable and
build manifest in ignored build-symbols/DEVELOPMENT_SHA256/ under this repository.
Keep that archive for the installed version; it survives later rebuilds/workdir cleanup.
The development workdir executable also remains untouched. Neither archive is shipped
to the utilities directory. Both artifacts retain the same ELF build ID; use the
archived unstripped file with GDB for source/line debugging. No separate debug file
is needed. The deployment receipt records both SHA-256 hashes and the archive path.
Atomic deployment still verifies hashes/build identity and destination startup. Default:
/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp
Use --destination /directory/qqbsp or QQBSP_DEPLOY_PATH to override. Stage a temporary
file in that directory, preserve executable permissions, verify loader/hash/identity,
then atomically replace only qqbsp and verify again. Preserve the previous executable
on failure. Report unavailable destinations/failures explicitly. Never overwrite
qbsp, vis, light, other utilities or their libraries. This validated local deployment
is authorized; publication, packaging and production editor integration are not.

## Native engine operation

QrustyQuake remains preferred. Read qartographer/NATIVE_ENGINE.md for the vkQuake
comparison and preserved evidence. The old apparent shutdown stall was interactive
quit UI: acceptance.cfg now sets `exitstyle 2` to bypass confirmation/exit screens.
No compiler or collision expectation changed to accommodate another engine.

Native-only validation, reusing existing compiler artifacts and consumed BSP29:

```sh
SDL_VIDEODRIVER=dummy python3 qartographer/native.py --work /tmp/qqbsp-work --artifact deployment --output /tmp/qqbsp-native-new --ordinary /tmp/qqbsp-release-existing/deployment/compatibility/ordinary.bsp
python3 qartographer/test_native.py
```

The dummy driver passed on the local installed Qrusty build; omit the environment
prefix for desktop operation. --engine and --id1 override the installed defaults;
validated_build.py also accepts them. Underlying command:
`qrustyquake -basedir OUTPUT -window -width 960 -height 640 -nosound +exec acceptance.cfg`.
The script preserves 1/72-second frames, speed 100, 144 movement waits and 72
ordinary-map waits. Stock stays at (-1400,-1664,180); P1 advances more than 100
units in Y, ends above Z=130 and grounded in WALK. Both server clocks must advance;
the BSP29 player must be alive and grounded. Original hull assertions remain.

Require exit 0 within 55 seconds, QQBSP_NATIVE_DONE, all saves and state assertions.
A timeout kills the isolated process group with SIGKILL, reaps it within 5 seconds,
records INCOMPLETE and fails. Nonzero exit or incomplete states fail. Retain logs,
process.json, results.json and saves; never treat paused input as a compiler defect.

To attach a matching normal-exit native PASS to a completed Tier 3 checkpoint:

```sh
python3 qartographer/tiers.py --tier 3 --work /tmp/qqbsp-work --artifact deployment --results /tmp/qqbsp-release-existing/deployment --resume-native /tmp/qqbsp-native-new
```

Binary/input/engine identity and normal-exit process receipt must match. Historical
saves without that receipt are inspection only and cannot promote Tier 3. vkQuake's
current script readiness differs; it is an unaccepted research alternative. Native
hull 2 is not covered by this player fixture: retain Tier 2 independent hulls 0/1/2.
