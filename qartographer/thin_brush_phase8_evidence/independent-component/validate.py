#!/usr/bin/env python3
from pathlib import Path
import json,time,sys
from oracle import analyze
E=Path(sys.argv[1]);cases=json.loads((E/'cases.json').read_text());actual=json.loads((E/'filtered-final.json').read_text());byname={r['name']:r for r in actual['results']};rows=[];failures=[]
# Identical permutations are independently checked against the same exact
# mathematical input-set result, not presumed correct from compiler equality.
cache={}
for case in cases:
    key=json.dumps({k:v for k,v in case.items() if k in ['planes','query','point','relation']},sort_keys=True)
    # Order-independent exact rational oracle is run once per effective system.
    canonical=json.dumps(dict(planes=sorted(set(tuple(p) for p in case['planes'])),**{k:case[k] for k in ['query','point','relation'] if k in case}),sort_keys=True)
    start=time.perf_counter()
    if canonical not in cache:cache[canonical]=analyze(case)
    oracle=cache[canonical];got=byname[case['name']];expected=oracle|case.get('component_expected',{})
    errors={k:dict(want=v,got=got.get(k)) for k,v in expected.items() if got.get(k)!=v}
    established={k:dict(want=v,got=oracle.get(k)) for k,v in case.get('established',{}).items() if oracle.get(k)!=v}
    if errors or established:failures.append(dict(name=case['name'],errors=errors,established=established))
    rows.append(dict(name=case['name'],oracle=oracle,component=expected,seconds=time.perf_counter()-start,errors=errors,established_errors=established))
    (E/'oracle-results.json').write_text(json.dumps(dict(rows=rows,failures=failures),indent=2)+'\n')
    print(case['name'],oracle,errors,established,flush=True)
print('PASS' if not failures else 'FAIL');sys.exit(bool(failures))
