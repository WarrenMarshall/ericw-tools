from pathlib import Path
import json,re,hashlib
E=Path('/tmp/qqbsp-phase6/evidence');load=lambda n:json.loads((E/n).read_text());oracle={r['name']:r['component'] for r in load('oracle-results.json')['rows']}
summary={};stable={}
for mode,file in [('filtered','filtered-final.json'),('double-exact','double-exact-final.json'),('exact','exact-final.json')]:
    data=load(file)['results'];bad=[]
    for r in data:
        for k,want in oracle[r['name']].items():
            if r.get(k)!=want:bad.append(dict(name=r['name'],key=k,want=want,got=r.get(k)))
        stable[r['name']]= {k:r.get(k) for k in oracle[r['name']]} if mode=='filtered' else stable[r['name']]
        if mode!='filtered':assert stable[r['name']]=={k:r.get(k) for k in oracle[r['name']]}
    assert not bad,bad
    sums={k:sum(r['stats'][k] for r in data) for k in ['fast','adaptive','exact','triples','exact_homogeneous_builds','exact_rank_constraints']};den=sum(sums[k] for k in ['fast','adaptive','exact'])
    summary[mode]=dict(cases=len(data),all_oracle_comparisons_pass=True,aggregate_ms=sum(r['microseconds'] for r in data)/1000,stats=sums,percentages={k:100*sums[k]/den for k in ['fast','adaptive','exact']},region_api_calls=sum(r['region_api_calls'] for r in data),worst_region_api_us=max(r['worst_region_api_us'] for r in data),worst_bundle_us=max(r['microseconds'] for r in data),allocation_calls=sum(r['allocation_calls'] for r in data),allocated_bytes=sum(r['allocated_bytes'] for r in data),peak_case_live_increment_bytes=max(r['peak_live_increment_bytes'] for r in data),bundles_with_exact_sign=sum(r['stats']['exact']>0 for r in data))
latency=load('latency-final.json')['results'];summary['latency_instrumented']=dict(worst_sign_ns=max(r['worst_sign_ns'] for r in latency),worst_case=max(latency,key=lambda r:r['worst_sign_ns'])['name'],note='Separate instrumented run: timer overhead included, ordinary throughput measurements do not enable sign timers.')
final=load('filtered-final.json')['results'];summary['witnesses']=[r for r in final if r['name'] in ['A-hull2-front','A-actual-post-csg-route','B-narrow-quadrilateral','C-sky-roof-gap','D-halloween-rounded-extent','E-p1-rounded-extent','F-rotated-portal','F-base-winding','F-make-portal']];summary['depth']=[r for r in final if r['name'].startswith('depth-')];summary['ordinary']=[r for r in final if r['name'] in ['ordinary-box','transformed-box','rotated-translated']]
# Independently checked permutations and duplicates preserve every decision field.
for r in final:
    parent=next((c.get('parent') for c in load('cases.json') if c['name']==r['name']),None)
    if parent:
        keys=['dimension','front_dimension','back_dimension','section_dimension','strict_front','strict_back','point_consistent','point_query_sign','relation']
        p=next(v for v in final if v['name']==parent)
        assert {k:r.get(k) for k in keys}=={k:p.get(k) for k in keys}
summary['permutation_duplicate_variants']=sum('parent' in c for c in load('cases.json'))
summary['source_routes']=load('source-route-results.json');summary['exact_extents']=load('exact-extents.json')
(E/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k in ['filtered','double-exact','exact','latency_instrumented','permutation_duplicate_variants']},indent=2))
for r in summary['witnesses']+summary['depth']+summary['ordinary']:print(r['name'],r['dimension'],r.get('front_dimension'),r.get('back_dimension'),r.get('section_dimension'),round(r['microseconds'],2),r['stats'])
