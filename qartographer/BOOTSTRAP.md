# QQBSP bootstrap — 2026-10-26

A validated Linux `qqbsp` development baseline is established and deployed locally.
This is not a production exporter migration or a portable compiler release.

## Source and build

- Branch: `qartographer/qqbsp-alpha10`; no remote pushes.
- Upstream: `ccaeb8457a1267860ebe99ed1df7394ebdd6b435`, peeled alpha10.
  Tag object, pristine archive hash and all three gitlinks match the investigation.
- Fresh official upstream fetch still resolves main to
  `36eec1da2a194467e6baac2f444c2dd04b57d266`. Later fill/default and other changes
  are deliberately excluded from this tested baseline. Original main is retained.
- P1: isolated commit `7f2ef6f32ce16ffc5b9167a57f5c7adad0ccdf58`; one functional
  argument changes to retain wholly ON support windings. No tolerance, actor-box,
  source-coordinate or BSP-format changes. P2 remains an unapplied candidate.
- Validated executable source: `72ea770193cef098c3b427648e6ee28ea130d737`.
  Subsequent changes concern validation/deployment/docs, not compiler algorithms.
- GCC 13.3.0, GNU ld 2.42, CMake 3.28.3, Ninja 1.11.1, Python 3.12.3;
  Ubuntu 24.04 x86_64/glibc 2.39. Both compilers use identical RelWithDebInfo
  configuration and flags per case. Build only QBSP and its validation dependencies.
- `baseline.json` pins submodules, Googletest, TBB 2021.11.0, Embree 4.4.0,
  JSON 3.12.0, archive checksums and fixtures. Embree is configure-only for QBSP.
  Full revisions, commands, runtime hashes and compiler identities are preserved
  in [evidence](evidence/qqbsp-build.json).

`qqbsp` and retained `qbsp` targets share one compiler library; no implementation
was duplicated. A downstream-built `qbsp` also contains P1, so stock comparisons
use the pristine archived baseline. `qqbsp -help` prints the upstream full SHA,
downstream full SHA and `patches=P1` alongside upstream's existing version banner.
The target naturally produces qqbsp.exe on Windows, but Windows is unvalidated.

## Regression results

| Check | Pristine alpha10 | P1 QQBSP |
| --- | ---: | ---: |
| Reduced four-brush oracle failures | 104 | 0 |
| Roller default, hulls 0 / 1 / 2 failures | 0 / 82 / 35 | 0 / 0 / 0 |
| Roller -chopfragment, hulls 0 / 1 / 2 failures | 0 / 84 / 42 | 0 / 0 / 0 |
| Halloween full-map oracle failures | 25 | 0 |
| Halloween models / faces / clipnodes | 94 / 16,424 / 27,275 | 94 / 16,424 / 26,296 |
| Halloween QBSP elapsed, one sequential trial | 13.056 s | 13.215 s |

Reduced hull checks: 421 / 420 / 421. Roller hull 0: 1,008 non-boundary samples;
actor hulls: both sides of support on 584 tracks each. Halloween: player/large
support 1,897 / 2,128; source-clear samples 973 / 764; all 10,070 point/projectile
comparisons pass. Source-obstructed samples remain separately tracked.
No sample or tolerance was relaxed. Timings differ by about +1.2%; this is not a
statistical performance claim. Six geometry/collision lumps match the earlier
investigation for both corresponding compilers, including P1-only versus its
historical P1+P2 build on the unchanged input. [Collision evidence](evidence/collision.json),
[historical comparison](evidence/historical-lumps.json).

All 13 selected unchanged upstream QBSP tests passed: ordinary sealed rooms,
duplicate/empty brushes, touching/shared boundaries, CSG, angled geometry, sealing
and mixed hull contents. Four historical thin-cell/opening cases pass independent
support and clearance checks for both actor hulls and CLIP/visual hull-0 semantics.

Fresh native matched WALK tests reproduce stock obstruction and P1 movement from
(-1400,-1664,180) to (-1400,-1502.543823,168.025421), grounded. An ordinary BSP29
was compiled by QQBSP, consumed by installed stock VIS and LIGHT (904 lightmap
bytes, zero empty lightmaps), and loaded in Quake with a grounded WALK player.
[Native states](evidence/native.json), [Tier 3 receipt](evidence/tier3.json).

Native engine shutdown stalled after all required saves, for both the installed
AppImage launcher and its extracted runtime. Test-only processes were forcibly
cleaned up. Completed saves were preserved and independently asserted using the
focused resume command; compiler/consumer tests were not repeated. This is a
recorded engine-teardown limitation, not a claim of clean engine exit. Missing or
invalid saved states still fail acceptance. Initial failure logs are retained.

Provenance discrepancy: the investigation's summary provenance.json lists a MAP
hash beginning `91593e…`. Its full-map/textured/export-equivalence evidence and
the preserved actual full-on.map agree on `16250e…`, which is pinned here. The
source archive, source/tag/gitlinks, P1 patch and Roller fixture identities match.
No authored MAP was changed. The now-unused, clean main-branch JSONcpp checkout
was moved to /tmp/qqbsp-bootstrap/initial-main-jsoncpp; alpha10 uses pinned JSON
FetchContent instead. Upstream submodule Git objects remain available.

## Deployment and operation

Validated `qqbsp` SHA-256:
`9a36f9b449da4484e7c13f87d4f72698a9b998fc42e3a9e21bd5e8624e068d1a`.
Pristine comparison SHA-256:
`b80a35bc57eee9906c259abf2aa30a475c6a3f0864b6e4f9c16f233f9658d880`.

Installed only at:
`/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp`.
Staged and final hash/build identity/startup matched, with loader override variables
cleared. Existing destination TBB libraries satisfy local startup; no libraries
were copied over them. Every pre-existing file in that utilities directory,
including qbsp/vis/light, is hash-identical to its original. Mode is executable.
Unavailable destination, protected stock filename, missing-runtime and injected
post-replacement failure checks all rejected safely and preserved the old file.
[Deployment](evidence/deployment.json), [preservation/runtime evidence](evidence/destination.json).

Use the exact tier/build/deployment commands in [AGENTS.md](../AGENTS.md) and
[README.md](README.md). Normal operation is validated_build.py; build.py alone
never promotes an experiment. deploy.py independently requires matching Tier 3
and collision PASS receipts. Override --destination or QQBSP_DEPLOY_PATH as needed.
The upstream merge/patch-retirement procedure is documented in README.md.

## Limits and next acceptance tests

This establishes pinned inputs and a repeatable Linux recipe, not independently
verified bit-for-bit binary reproducibility, an older-glibc portability guarantee,
or Windows/macOS packaging. It is a bounded QBSP regression suite, not exhaustive
upstream/compiler certification. VIS/LIGHT implementation and tests were untouched.
No production exporter, authored map, installed stock compiler or game asset changed.
Full authored Halloween gameplay/lighting acceptance is still outstanding; the
ordinary fixture and Roller native tests do not substitute for that work.

Before adopting direct Spline collision or deleting workarounds:

1. Accept exact collision semantics in place of the optional regularized envelope.
2. Check remaining Spline profiles, thin supports, intentional gaps/joins, transformed
   and shared occurrences, plus player and large-actor hulls against source geometry.
3. Play the changed full export natively: traverse the historical walls/floor and
   RollerSpline, check snags, support and monster clearance, and retain hull-0 checks.
4. Separately test the original uncanonicalized near-axial long-wall reproduction.
5. Check representative final VIS/light/texture results using stock consumers;
   consider P2 only as a separate capability if independent actor geometry remains.

Keep all current exporter workarounds until those acceptance decisions are complete.
