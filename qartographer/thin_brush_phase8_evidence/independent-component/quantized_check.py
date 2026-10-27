from pathlib import Path
import json,sys
from oracle import analyze,range_on_plane
E=Path(sys.argv[1]);cases=json.loads((E/'bsp-quantized-cases.json').read_text());actual={r['name']:r for r in json.loads((E/'bsp-quantized-results.json').read_text())['results']};rows=[]
for c in cases:
    expected=analyze(c);r=actual[c['name']]
    assert all(r.get(k)==v for k,v in expected.items()),(c['name'],r,expected)
    row=dict(name=c['name'],oracle=expected)
    if c['name'].startswith(('D-','E-')):row['extent']=range_on_plane(c['planes'],c['query'])
    rows.append(row)
(E/'bsp-quantized-oracle.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS: seven target-plane models agree with exact oracle')
