#!/usr/bin/env python3
"""Independent BSP certification for spline_collision_thin_cell_test exports.
Reuses the established BSP reader and convex configuration-space oracle.
Usage: python3 tests/helpers/spline_thin_collision_compile.py /path/to/qbsp [directory]
"""
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('collision', Path(__file__).with_name('spline_smooth_collision_compile.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
D = Path(sys.argv[2] if len(sys.argv) > 2 else '/tmp/qart-spline-thin')
QB = sys.argv[1]
results = {}


def compile_map(name):
    started = time.monotonic()
    p = subprocess.run([QB, '-chopfragment', '-bsp2', '-notex', '-nopercent', str(D / (name + '.map'))], capture_output=True, text=True)
    (D / (name + '-qbsp.log')).write_text(p.stdout + p.stderr)
    assert p.returncode == 0, (name, p.stdout, p.stderr)
    return c.BSP(D / (name + '.bsp')), time.monotonic() - started


def any_solid(bsp, point, hull):
    for model in range(bsp.models()):
        # Quake bmodel brushes retain world coordinates in these static exports.
        at = bsp.l[14][0] + model * 64
        import struct
        lo = struct.unpack_from('<3f', bsp.b, at)
        hi = struct.unpack_from('<3f', bsp.b, at + 12)
        radius = (0, 0, 0) if hull == 0 else ((16, 16, 32) if hull == 1 else (32, 32, 64))
        if any(point[i] < lo[i] - radius[i] - 1 or point[i] > hi[i] + radius[i] + 1 for i in range(3)):
            continue
        if bsp.contents(point, model, hull) == -2:
            return True
    return False


def check_case(name, solids, bsp, seconds):
    vertices = [c.quake(v) for s in solids for f in s for v in f['v']]
    centers = [tuple(sum(c.quake(v)[i] for f in s for v in f['v']) / sum(len(f['v']) for f in s) for i in range(3)) for s in solids]
    lo = [min(v[i] for v in vertices) - 48 for i in range(3)]
    hi = [max(v[i] for v in vertices) + 48 for i in range(3)]
    points = centers + [tuple(lo[i] + c.halton(k, [2, 3, 5][i]) * (hi[i] - lo[i]) for i in range(3)) for k in range(1, 513)]
    counts = {}
    failures = []
    for hull, radius, offset in [(1, (16, 16, 28), 4), (2, (32, 32, 44), 20)]:
        cells = [c.supports(s, radius) for s in solids]
        checked = 0
        for p in points:
            distance = c.margin((p[0], p[1], p[2] + offset), cells)
            # Outside the existing 0.08119-unit envelope plus compiler epsilon.
            if abs(distance) < .2:
                continue
            checked += 1
            if any_solid(bsp, p, hull) != (distance < 0):
                failures.append({'hull': hull, 'p': p, 'source_margin': distance})
        counts[str(hull)] = checked
    assert not failures, (name, failures[:10])
    if name == 'essential-floor':
        for hull in [1, 2]:
            assert bsp.contents((0, 64, 24), hull=hull) == -2, ('lost essential sub-grid support', hull)
            assert bsp.contents((0, 64, 24.25), hull=hull) == -1, ('inflated essential floor', hull)
    if name.startswith('passage-'):
        width = int(name.split('-')[1]) + .25
        hull = 1 if width < 64 else 2
        assert bsp.contents((8 + width / 2, 64, 0), hull=hull) == -1, ('closed intentional opening', name)
    # World CLIP has no projectile contribution, even for the recovered wedge.
    for p in (centers[:-1] if name.startswith("passage-") else centers):
        assert bsp.contents(p, hull=0) == -1, (name, 'CLIP changed hull 0')
        for model in range(1, bsp.models()):
            assert bsp.contents(p, model, 1) == -1 and bsp.contents(p, model, 2) == -1, (name, 'detail generated actor hull')
    results[name] = {'actor_samples': counts, 'compile_seconds': seconds, 'source_cells': len(solids)}
    print(name, results[name], 'PASS', flush=True)


def height(x, y, cells):
    heights = []
    for planes in cells:
        low, high = -math.inf, math.inf
        for n, d in planes:
            v = d - n[0] * x - n[1] * y
            if abs(n[2]) < 1e-8:
                if v < -1e-5:
                    break
            elif n[2] > 0:
                high = min(high, v / n[2])
            else:
                low = max(low, v / n[2])
        else:
            if high > low + .001 and math.isfinite(high):
                heights.append(high)
    return max(heights) if heights else None


if (D / 'full-on.bsp').exists():
    full = json.loads((D / 'full-geometry.json').read_text())
    old, new = c.BSP(D / 'full-off.bsp'), c.BSP(D / 'full-on.bsp')
    floor_id = 'ee2625bf-6804-4384-a272-214b8011f60b'
    floor = [r['faces'] for r in full if r['spline'] and r['item'] == floor_id]
    vs = [c.quake(v) for s in floor for f in s for v in f['v']]
    xmin, xmax = min(v[0] for v in vs), max(v[0] for v in vs)
    ymin, ymax = min(v[1] for v in vs), max(v[1] for v in vs)
    # Include all local geometry when judging a passage; the floor alone cannot
    # describe surrounding static walls or other constructions.
    nearby = [r['faces'] for r in full if any(xmin - 100 < c.quake(v)[0] < xmax + 100 and ymin - 100 < c.quake(v)[1] < ymax + 100 for f in r['faces'] for v in f['v'])]
    report = {}
    projectile_samples = 0
    failures = []
    for hull, radius, offset in [(1, (16, 16, 28), 4), (2, (32, 32, 44), 20)]:
        cells = [c.supports(s, radius) for s in floor]
        obstacles = [c.supports(s, radius) for s in nearby]
        support, accessible, inherited_blocked = 0, 0, 0
        for x in range(math.ceil(xmin) + 4, math.floor(xmax), 12):
            for y in range(math.ceil(ymin) + 4, math.floor(ymax), 12):
                top = height(x, y, cells)
                if top is None:
                    continue
                p = (x, y, top - offset - .3)
                if c.margin((x, y, p[2] + offset), cells) < -.15:
                    support += 1
                    if new.contents(p, hull=hull) != -2:
                        failures.append(('missing_floor_support', hull, p))
                above = (x, y, top - offset + .3)
                source_gap = c.margin((x, y, above[2] + offset), obstacles)
                if source_gap > .2:
                    accessible += 1
                    if any_solid(new, above, hull):
                        failures.append(('new_obstruction', hull, above, source_gap))
                else:
                    inherited_blocked += 1
                if hull == 1:
                    for dz in [-48, -24, 0, 24, 48]:
                        q = (x, y, top - offset + dz)
                        projectile_samples += 1
                        if any_solid(old, q, 0) != any_solid(new, q, 0):
                            failures.append(('hull0_changed', q))
        report[str(hull)] = {'support': support, 'accessible_above_floor': accessible, 'source_obstructed_above_floor': inherited_blocked}
    (D / 'oracle-failures.json').write_text(json.dumps(failures, indent=2))
    (D / 'full-counts.json').write_text(json.dumps({'actor_tracks': report, 'equal_projectile_samples': projectile_samples}, indent=2))
    assert not failures, failures[:20]
    assert all(v['support'] > 100 and v['accessible_above_floor'] > 100 for v in report.values()), report
    results['full-map'] = {'actor_tracks': report, 'equal_projectile_samples': projectile_samples}
    print('full-map', results['full-map'], 'PASS', flush=True)

(D / 'compiled-thin-results.json').write_text(json.dumps(results, indent=2) + '\n')
print('Compiled thin-cell recovery PASS')
