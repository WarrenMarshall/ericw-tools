# Native engine investigation — 2026-10-26

**Keep QrustyQuake as the preferred QQBSP native test engine.** Setting
`exitstyle 2` makes the installed engine quit unattended with exit status 0,
without changing the fixtures, saved starts, movement inputs or collision assertions.
Its software renderer also passes the same tests with SDL's dummy video driver.
There is no demonstrated reason to force a vkQuake migration. Further vkQuake
adaptation stopped at the user's direction.

## Comparison and decision

Located installed AppImages at
`~/.local/share/Steam/steamapps/common/Quake/{qrustyquake,vkQuake}` and already
extracted runtimes under /tmp. vkQuake identifies itself as **1.35.0**. Both
installed and extracted artifact hashes, exact invocations, logs, saves and input
hashes are retained in [native_engine_evidence](native_engine_evidence/summary.json).
No engine was installed, rebuilt or modified.

All engine comparisons used the same existing stock/P1 RollerSpline BSPs, matched
seed saves, standard id1 PAKs and existing ordinary BSP29. Inputs were private copies
or read-only PAK symlinks. Compiler algorithms, exporter and authored maps did not
change. Original timing remains `host_framerate 0.013888889`, `host_maxfps 72`,
100-unit movement speed, 144 wait commands per movement and 72 for the ordinary map.

| Case | QrustyQuake | vkQuake 1.35.0 |
| --- | --- | --- |
| Original harness | Required saves complete; quit remains interactive; killed at diagnostic timeout | Exits 0 in 7.44 s, but Roller simulation does not advance and ordinary save is rejected |
| Explicit console before quit | Still waits on interactive exit screen | Clean exit; native assertions still not satisfied |
| Unattended Qrusty profile (`exitstyle 2`) | Clean exit 0, correct movement/grounding | No equivalent accepted profile established |
| Final native entry point, extracted runtime | PASS, exit 0 in 5.67 s | Not selected |
| SDL dummy video, extracted Qrusty runtime | PASS, exit 0 in 5.22 s | Not investigated further |
| SDL dummy video, installed Qrusty AppImage | PASS, exit 0 in 5.27 s | Not investigated further |

These are bounded individual trials, not engine reliability statistics.

Qrusty reproduces the existing negative control: stock stays at
`(-1400,-1664,180)`. P1 moves from that identical start to
`(-1400,-1502.543823,168.025421)`, ordinary WALK, grounded (`flags & 512`).
The server clock advances from 3.286111 to 5.272222. The BSP29 player is alive,
grounded at `(-56,-96,88.031250)`. No collision assertion was weakened; the harness
now additionally checks simulation progress and ordinary-map health/grounding.

vkQuake parses the BSPs and writes inspectable version-5 saves. In the unchanged
script, however, both Roller endpoints have the *same* server time and position;
the local client remains unconnected/unspawned, and `save ordinary_start` reports
that the player is dead. Exit status 0 alone is therefore insufficient. Explicit
menu/game state, a 72-frame load warmup, and protocol 666 matching Qrusty did not
establish equivalent sign-on/gameplay. The exact cause of this vkQuake-specific
readiness interaction remains unresolved. It is **not** evidence against QQBSP
collision correctness, nor a general claim that vkQuake cannot load BSP29/BSP2.
We did not change movement expectations or add engine-specific allowances to pass it.

The existing native fixture exercises the player/hull 1. It does not exercise a
native large monster/hull 2 in either engine. The unchanged Tier 2 independent
hull-0/1/2 collision oracles remain required; changing engine cannot substitute for
those expectations. No new native hull-2 or projectile coverage is claimed.

## Cause of the apparent Qrusty shutdown stall

The old harness sent `quit` from gameplay without configuring unattended exit.
Qrusty's normal quit path can enter the confirmation menu. Even explicit console
quit can enter its interactive VGA-style exit screen. `exitstyle 2` bypasses both.
The controlled and final runs exit normally with that setting and retain exactly
the expected movement states. This identifies an **engine/harness interaction with
interactive quit UI**, not a demonstrated shutdown deadlock or AppImage/FUSE defect.
Extraction alone was not the fix.

Relevant official source references: QrustyQuake
[quit command](https://github.com/cyanbun96/qrustyquake/blob/v0.8.3/src/host_cmd.c),
[quit menu](https://github.com/cyanbun96/qrustyquake/blob/v0.8.3/src/menu.c),
[exit screen](https://github.com/cyanbun96/qrustyquake/blob/v0.8.3/src/sys_sdl.c);
vkQuake [load/sign-on](https://github.com/Novum/vkQuake/blob/1.35.0/Quake/host_cmd.c)
and [server frame](https://github.com/Novum/vkQuake/blob/1.35.0/Quake/host.c).
These explain relevant paths; a matching Qrusty release-source provenance for the
installed binary is not claimed. Runtime behavior and binary hashes are the evidence.

## Operational commands

The standard Tier 3/validated build workflow still selects installed QrustyQuake.
For a native-only check using already validated compiler artifacts and the existing
stock-VIS/LIGHT-consumed BSP29 (use fresh output directories):

```sh
SDL_VIDEODRIVER=dummy python3 qartographer/native.py \
  --work /tmp/qqbsp-work --output /tmp/qqbsp-native-new \
  --ordinary /tmp/qqbsp-tier3-existing/compatibility/ordinary.bsp
```

Omit SDL_VIDEODRIVER=dummy for a normal desktop window. Override --engine and --id1
for another Qrusty installation. An extracted AppRun is optional, not a quit fix.
Exact underlying invocation:

```sh
/path/to/qrustyquake -basedir /tmp/qqbsp-native-new \
  -window -width 960 -height 640 -nosound +exec acceptance.cfg
```

Generated acceptance.cfg sets `exitstyle 2`, preserves the historical native input
sequence, saves both starts/ends and the ordinary state, then emits
`QQBSP_NATIVE_DONE` and quits. The runner requires exit 0 within **55 seconds**,
the marker, complete parseable saves and every collision/state assertion. On timeout
it kills the isolated process group with SIGKILL, reaps it within 5 seconds, records
INCOMPLETE in process.json and exits nonzero. Existing saves cannot turn that run
into an unattended PASS. Nonzero exit, missing saves or paused simulation also fail.
Native environment/command/exit/timing are retained alongside saves and engine hashes.

To attach a fresh native-only PASS to an otherwise completed Tier 3 checkpoint:

```sh
python3 qartographer/tiers.py --tier 3 --work /tmp/qqbsp-work \
  --results /tmp/qqbsp-tier3-existing --resume-native /tmp/qqbsp-native-new
```

A matching process PASS/zero-exit/no-timeout receipt and binary/input/engine identities
are required. Historical timeout saves can still be inspected, but cannot promote a
Tier 3 receipt. Normal-exit attachment and historical-rejection paths were verified
without repeating the earlier passing compiler regressions. Two fast mocked lifecycle
regressions exercise timeout group cleanup and nonzero-exit rejection:

```sh
python3 qartographer/test_native.py
```

This assignment performed native infrastructure validation only. It did not rebuild
or redeploy QQBSP, rerun unrelated compiler/VIS/LIGHT suites, or modify installed games.
Qrusty headless success is specific to this tested build/SDL backend, not a portability
promise. vkQuake remains an optional research comparison; it is not an accepted
replacement for the native gate until equivalent behavior is demonstrated.
