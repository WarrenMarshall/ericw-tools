from pathlib import Path
import json,sys
E=Path(sys.argv[1]);oracle={r['name']:r['component'] for r in json.loads((E/'oracle-results.json').read_text())['rows']}
for filename in ['filtered-final.json','double-exact-final.json','exact-final.json']:
    for r in json.loads((E/filename).read_text())['results']:
        for key,want in oracle[r['name']].items():assert r.get(key)==want,(filename,r['name'],key,r.get(key),want)
print('PASS: filtered, double+exact and exact-only agree with the independent oracle')
