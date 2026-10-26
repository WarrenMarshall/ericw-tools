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


for name, solids in json.loads((D / 'geometry.json').read_text()).items():
    bsp, seconds = compile_map(name)
    check_case(name, solids, bsp, seconds)
(D / 'results.json').write_text(json.dumps(results, indent=2)+'\n')
