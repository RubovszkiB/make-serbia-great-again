"""Read native province bitmap adjacency; no map files are modified."""
import csv
import hashlib,json
from PIL import Image
import numpy as np
from pathlib import Path
TFR=Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356')
from validate_phase1 import parse,get
defs=list(csv.reader((TFR/'map/definition.csv').read_text().splitlines(),delimiter=';'))
colors={int(r[0]):int(r[1])+(int(r[2])<<8)+(int(r[3])<<16) for r in defs if len(r)>4 and r[0].isdigit()}
reverse={c:p for p,c in colors.items()}
states={}
for p in (TFR/'history/states').glob('*.txt'):
 try:a=get(parse(p.read_text(encoding='utf-8-sig',errors='replace')),'state');id=int(get(a,'id'));states.update({int(k):id for k,o,v in get(a,'provinces')})
 except (AssertionError,StopIteration,ValueError):pass
a=np.array(Image.open(TFR/'map/provinces.bmp'))[:,:,:3].astype(np.uint32);a=a[:,:,0]+(a[:,:,1]<<8)+(a[:,:,2]<<16)
result={}
for p in [6940,9849,9874,9890,14402,14400,14401]:
 mask=a==colors[p];neighbors=set()
 for b,c in [(a[:,:-1],mask[:,1:]),(a[:,1:],mask[:,:-1]),(a[:-1,:],mask[1:,:]),(a[1:,:],mask[:-1,:])]:
  neighbors.update(int(v) for v in np.unique(b[c]))
 result[p]=sorted((reverse[c],states.get(reverse[c])) for c in neighbors if c in reverse and c!=colors[p])
assert any(state in [44,105,106] for province,state in result[9849])
assert any(state==105 for province,state in result[14401])
report={'native_map_adjacency_validation':'passed','province_neighbors_with_state_ID':result,'fort_provinces':[9849,14401],'forts_border_Pact_states':[44,105,106],'provinces_bmp_sha256':hashlib.sha256((TFR/'map/provinces.bmp').read_bytes()).hexdigest(),'definition_csv_sha256':hashlib.sha256((TFR/'map/definition.csv').read_bytes()).hexdigest()}
Path('docs/encirclement_map_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Native province bitmap adjacency verified: forts 9849 and 14401 border Pact territory.')
