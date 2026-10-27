import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True
base=Path('/tmp/qqbsp-phase7');sys.path.insert(0,str(base/'phase6/component'))
from oracle import analyze
cases=json.loads((base/'source/qartographer/phase7-cases.json').read_text());rows=[]
for c in cases:
 start=time.monotonic();got=analyze(c);want=c['established'];errors={k:[want[k],got.get(k)] for k in want if got.get(k)!=want[k]}
 rows.append(dict(name=c['name'],oracle=got,seconds=time.monotonic()-start,errors=errors));print(c['name'],errors,flush=True)
(base/'evidence/integrated-oracle-replay.json').write_text(json.dumps(dict(rows=rows,pass_=not any(r['errors'] for r in rows)),indent=2)+'\n')
assert not any(r['errors'] for r in rows)
