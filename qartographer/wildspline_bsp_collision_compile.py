#!/usr/bin/env python3
"""Independent reduced WildSpline MAP/configuration-space versus BSP regression.

Usage: python3 tests/helpers/wildspline_bsp_collision_compile.py QBSP OUTPUT
The stock alpha10 compiler fails this test. See the documented external defect
and candidate patch; failure is intentional regression protection, not skipped.
"""
import argparse
import itertools
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
import spline_smooth_collision_compile as c

FIXTURE = Path(__file__).resolve().parent / 'fixtures/reduced.map'
SAMPLE = (-1844, -185, 54.750525691416364)
HULLS = [(0, (0, 0, 0), 0), (1, (16, 16, 28), 4), (2, (32, 32, 44), 20)]


def brushes(text):
    result = []
    for body in re.findall(r'\{([^{}]+)\}', text):
        planes = []
        clip = False
        for line in body.splitlines():
            vs = [tuple(map(float, m.split())) for m in re.findall(r'\(([^()]*)\)', line)]
            if len(vs) != 3:
                continue
            clip |= bool(re.search(r'\) CLIP ', line))
            n = c.norm(c.cross(c.sub(vs[0], vs[1]), c.sub(vs[2], vs[1])))
            assert n is not None
            planes.append((n, c.dot(n, vs[0])))
        if not planes:
            continue
        vertices = []
        for (a, da), (b, db), (d, dd) in itertools.combinations(planes, 3):
            determinant = c.dot(a, c.cross(b, d))
            if abs(determinant) < 1e-12:
                continue
            bc, dc, ab = c.cross(b, d), c.cross(d, a), c.cross(a, b)
            v = tuple((da * bc[i] + db * dc[i] + dd * ab[i]) / determinant for i in range(3))
            if all(c.dot(n, v) - distance <= 1e-7 for n, distance in planes):
                if not any(c.dot(c.sub(v, old), c.sub(v, old)) < 1e-12 for old in vertices):
                    vertices.append(v)
        assert len(vertices) >= 4
        # Complete polytope + AABB Minkowski support directions. All pairs are
        # conservative candidates; only actual supporting directions survive.
        normals = [n for n, _ in planes]
        normals += [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
        for a, b in itertools.combinations(vertices, 2):
            for axis in [(1,0,0),(0,1,0),(0,0,1)]:
                n = c.norm(c.cross(c.sub(b, a), axis))
                if n is None:
                    continue
                values = [c.dot(n, v) for v in vertices]
                edge = c.dot(n, a)
                if max(values) - edge < 1e-7:
                    normals.append(n)
                if edge - min(values) < 1e-7:
                    normals.append(tuple(-x for x in n))
        result.append((clip, vertices, normals))
    return result


def expanded(brush, radius):
    _, vertices, normals = brush
    return [(n, max(c.dot(n, v) for v in vertices) + sum(abs(n[i])*radius[i] for i in range(3))) for n in normals]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('qbsp')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / 'wildspline.map'
    shutil.copyfile(FIXTURE, path)
    text = path.read_text()
    assert text.count('"classname" "func_detail"') == 1
    assert text.count('CLIP [') == 48  # Exact two original proxies, no inflation.
    assert '[ ' in text and ' ] 0 1 1' in text  # Original Valve 220 mappings.
    geometry = brushes(text)
    assert len(geometry) == 4
    process = subprocess.run([args.qbsp, '-chopfragment', '-bsp2', '-notex', '-nopercent', str(path)], capture_output=True, text=True)
    (args.output / 'compile.log').write_text(process.stdout + process.stderr)
    assert process.returncode == 0, process.stdout + process.stderr
    bsp = c.BSP(path.with_suffix('.bsp'))
    assert bsp.models() == 1  # Detail merged into world; no bmodel routing trick.
    points = [SAMPLE, (-1844,-173,52.68060776696018), (-1832,-197,56.820443615872556), (-1832,-161,53.370580408445576)]
    # Both sides of the original floor boundary, neighboring static side, and
    # a continuous horizontal movement track across the disputed region.
    points += [(SAMPLE[0], SAMPLE[1], SAMPLE[2]+dz) for dz in [-1,-.6,-.3,0,.3,.6,1,4,16]]
    points += [(x,-185,SAMPLE[2]+dz) for x in range(-1960,-1759,2) for dz in [0,1,8,32]]
    points += [tuple(sum(v[i] for v in vs)/len(vs) for i in range(3)) for _,vs,_ in geometry]
    failures = []
    report = {}
    for hull, radius, offset in HULLS:
        cells = [expanded(b, radius) for b in geometry if hull != 0 or not b[0]]
        checked = 0
        for p in points:
            margin = c.margin((p[0],p[1],p[2]+offset), cells)
            # The MAP itself is the reference here, not a displaced proxy.
            # Avoid compiler contact uncertainty, retaining the disputed sample.
            if abs(margin) < .1:
                continue
            checked += 1
            actual = bsp.contents(p, hull=hull)
            if (actual == -2) != (margin < 0):
                failures.append({'hull': hull, 'point': p, 'map_margin': margin, 'contents': actual})
        report[str(hull)] = {'checked': checked, 'original_contents': bsp.contents(SAMPLE,hull=hull)}
    result = {'hulls': report, 'failures': failures}
    (args.output / 'results.json').write_text(json.dumps(result,indent=2)+'\n')
    assert not failures, failures[:10]
    print(json.dumps(report,indent=2))
    print('Reduced MAP/BSP collision regression PASS')


if __name__ == '__main__':
    main()
