# Qartographer QQBSP

This is a small downstream EricW Tools compiler fork, not a new compiler or a
fork of light/VIS. The supported artifact is `qqbsp` (`qqbsp.exe` on Windows).
Retain upstream's `qbsp` target; both targets share compiler code. A `qbsp` built
on this downstream branch also includes our corrections. Use a pristine source
snapshot for stock comparisons. Never install over the user's stock tools.

Keep conventional MAP input, standard Quake BSP output, and existing engine/tool
compatibility. Do not add formats, engine hooks, exporter adaptations, speculative
collision repairs, or threaded execution paths without explicit scope approval.
P1 is the accepted correction. P2 in qartographer/P2-unapplied.patch is only a
candidate; do not apply it as part of maintenance.

Keep each compiler correction in a separate commit, with a source explanation
and a regression that fails before and passes after. Build/identity and workflow
changes belong in separate commits. Preserve upstream notices and licenses.

Read qartographer/README.md and baseline.json before building. Use the pinned
Linux recipe, configure before recording a binary identity, and record source,
dependencies, flags, toolchain, hashes and results. Do not claim bit-for-bit
reproducibility from one build or confuse a dependency needed by CMake with a
runtime dependency. No production editor integration by default; validated local deployment is authorized.

For a local P1-path correction run the reduced and frozen Roller tests with
regress.py. Run --full for a baseline upgrade, release candidate, or changes to
shared winding/hull/BSP behavior. Research probes report failures as data;
regress.py is the assertive acceptance entry point. Do not weaken oracles or
silently skip expected stock failures. Expand upstream degenerate/coplanar and
contents coverage when the change creates that risk; ordinary docs/build edits
need only relevant checks. Native engine and full lighting acceptance are separate
release/adoption gates, not implied by occupancy tests.

For upstream updates follow the merge/patch retirement procedure in README.md;
never reset this branch to upstream or blindly apply a patch already in history.

Do not spawn sub-agents by default. Keep validation proportional and stop once
the changed behavior and material risks are demonstrated.

## Build, validate and deploy

The authorized local workflow automatically deploys only after full validation:

```
python3 qartographer/validated_build.py --work /tmp/qqbsp-work --results /tmp/qqbsp-results-new
```

For separate steps:

```
python3 qartographer/build.py --work /tmp/qqbsp-work --pristine
python3 qartographer/build.py --work /tmp/qqbsp-work
python3 qartographer/regress.py /tmp/qqbsp-work/pristine-build/qbsp/qbsp /tmp/qqbsp-work/patched-build/qbsp/qqbsp /tmp/qqbsp-results-new --full
python3 qartographer/deploy.py --work /tmp/qqbsp-work --results /tmp/qqbsp-results-new
```

Default deployment is
/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp.
Use --destination or QQBSP_DEPLOY_PATH to configure it. Never deploy a dirty or
unvalidated build, replace qbsp/vis/light, or overwrite their runtime libraries.
Deployment stages in the destination directory, tests its actual loader/startup,
then atomically replaces only qqbsp and verifies hash/build identity. Report
failures explicitly and preserve the previous working executable. See README.md
for dependency provisioning and limitations. This local deployment is authorized;
publication, packaging and production editor integration remain separately scoped.

## Strict project scope — QQBSP only

This fork exists exclusively to develop and maintain QQBSP, Qartographer's
customized EricW QBSP. In scope are QBSP geometry/collision correctness, shared
code directly required by QBSP, minimal CMake changes for qqbsp, QBSP-specific
regressions/benchmarks/diagnostics, identity, provenance and deployment.

VIS and LIGHT functionality, algorithms, performance, source, tests and build
behavior are out of scope. Do not modify them. Light preview, texture utilities,
other EricW applications, repository modernization, unrelated upstream bugs,
speculative optimization and distribution of a customized complete toolchain are
also out of scope. Existing stock utilities remain authoritative for those stages.

Build only targets required to produce and validate qqbsp: qqbsp and its shared
dependencies, plus pristine qbsp for comparison. Do not run whole-toolchain builds
or package targets. CMake may require configure-time dependencies for other tools;
that does not authorize compiling or changing those tools. Shared-source changes
require a demonstrated QBSP defect, narrow scope and independent testing. Do not
rewrite shared libraries merely to simplify this fork.

Success means an independently identifiable, validated qqbsp accepting standard
Quake MAP and emitting standard Quake BSP, correcting demonstrated defects with
a small maintainable patch set. Upstream source remains intact outside this scope.
