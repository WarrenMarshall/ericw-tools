from pathlib import Path
p=Path('/tmp/qqbsp-phase7/source/qartographer/thin_brush_probe.py')
t=p.read_text()
t=t.replace("results={}\nfor name,text in cases.items():", "results={}\ncases={k:v for k,v in cases.items() if k in ['rotated','adjacent','overlap','near-coplanar']}\nfor name,text in cases.items():")
t=t.replace("  d=out/(name+'-'+mode);", "  if name=='rotated' and mode=='default':continue # unchanged failure retained by original runner\n  d=out/(name+'-'+mode);")
t=t.replace("(d/'compile.log').write_text(r.stdout+r.stderr);assert r.returncode==0,name", """(d/'compile.log').write_text(r.stdout+r.stderr)
  if r.returncode:
   results[d.name]={'compile_exit':r.returncode,'failures':[{'kind':'compile failure'}]}
   (out/'results.json').write_text(json.dumps(results,indent=2)+'\\n')
   print(d.name,'COMPILE FAIL',flush=True)
   continue""")
# __file__ stays at the frozen oracle/fixture location; only failure aggregation changes.
exec(compile(t,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
