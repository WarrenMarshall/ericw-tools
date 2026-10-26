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
# Build qqbsp plus the QBSP-only upstream test target.
python3 qartographer/build.py --work /tmp/qqbsp-work
# Tier 1: relevant changes, frequent development checks.
python3 qartographer/tiers.py --tier 1 --work /tmp/qqbsp-work --results /tmp/qqbsp-tier1-new
# Tier 2: before accepting a compiler change; includes applicable Tier 1 checks.
python3 qartographer/tiers.py --tier 2 --work /tmp/qqbsp-work --results /tmp/qqbsp-tier2-new
# Tier 3: before promotion; includes Tier 1/2 and release checks.
python3 qartographer/tiers.py --tier 3 --work /tmp/qqbsp-work --results /tmp/qqbsp-tier3-new
# Deploy independently only from a matching Tier 3 PASS receipt.
python3 qartographer/deploy.py --work /tmp/qqbsp-work --results /tmp/qqbsp-tier3-new
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

Deployment requires a clean committed build, matching full Tier 3 PASS receipt,
matching hashes/build identity, and successful destination startup. Default:
/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp
Use --destination /directory/qqbsp or QQBSP_DEPLOY_PATH to override. Stage a temporary
file in that directory, preserve executable permissions, verify loader/hash/identity,
then atomically replace only qqbsp and verify again. Preserve the previous executable
on failure. Report unavailable destinations/failures explicitly. Never overwrite
qbsp, vis, light, other utilities or their libraries. This validated local deployment
is authorized; publication, packaging and production editor integration are not.

If an engine stalls only during shutdown after writing all complete native states,
the runner forcibly cleans up its process group and records that limitation; all
state assertions still apply. Incomplete/missing states fail. To inspect completed
states after a shutdown failure without rerunning passing compiler checks:

```sh
python3 qartographer/tiers.py --tier 3 --work /tmp/qqbsp-work --results /tmp/qqbsp-tier3-new --resume-native /tmp/qqbsp-tier3-new/native --engine /path/to/extracted/AppRun
```

The resume command requires the earlier successful compatibility checkpoint and
matching binary/input identities. Prefer --engine /path/to/extracted/AppRun for
AppImage/FUSE problems; validated_build.py also accepts --engine and --id1.
