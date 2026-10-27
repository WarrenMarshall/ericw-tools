from pathlib import Path
p=Path('/tmp/qqbsp-p3/source/qbsp/brushbsp.cc')
s=Path('/tmp/qqbsp-phase2/rejected-brushbsp.cc').read_text()
s=s.replace('const double side_epsilon = node_volume ? DIST_EPSILON : 0.1;', 'const double side_epsilon = DIST_EPSILON;')
s=s.replace('const double edge_epsilon = node_volume ? DIST_EPSILON : 0.02;', 'const double edge_epsilon = DIST_EPSILON;')
s=s.replace('w = w->clip_back(face.get_plane());','w = w->clip_back(face.get_plane(), DIST_EPSILON);')
p.write_text(s)
