import pathlib,json,struct
r=pathlib.Path('/tmp/qqbsp-phase3');rows=json.load(open(r/'reproduction.json'))
for row in rows:
 p=r/(row['compiler']+('-nofill' if row['nofill'] else ''))/row['mode']/(row['mode']+'.bsp');b=p.read_bytes();l=[struct.unpack_from('<ii',b,4+8*i) for i in range(15)];sets=[]
 for hull in [1,2]:
  seen=set();todo=[struct.unpack_from('<i',b,l[14][0]+i*64+36+4*hull)[0] for i in range(row['models'])]
  while todo:
   n=todo.pop()
   if n<0 or n in seen:continue
   seen.add(n);_,a,c=struct.unpack_from('<iii',b,l[9][0]+12*n);todo.extend((a,c))
  sets.append(seen)
 row['reachable_clipnodes']={'hull1':len(sets[0]),'hull2':len(sets[1]),'shared':len(sets[0]&sets[1]),'unreferenced':row['clipnodes']-len(sets[0]|sets[1])}
 print(row['compiler'],row['mode'],row['nofill'],row['reachable_clipnodes'])
(r/'reproduction.json').write_text(json.dumps(rows,indent=2)+'\n')
