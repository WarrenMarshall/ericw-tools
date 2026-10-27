from pathlib import Path
import json,sys
from oracle import range_on_plane
E=Path(sys.argv[1]);out={}
for c in json.loads((E/'cases.json').read_text()):
    if c['name'] in ['A-hull2-front','D-halloween-rounded-extent','E-p1-rounded-extent','F-rotated-portal']:
        out[c['name']]=range_on_plane(c['planes'],c['query'])
(E/'exact-extents.json').write_text(json.dumps(out,indent=2)+'\n')
