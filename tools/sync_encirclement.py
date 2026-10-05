"""After live validation, synchronize precisely the authorized 0.11 deployment."""
import hashlib,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LIVE=Path(r'C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again')
def inventory(root):return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
def main():
 sources=json.loads((ROOT/'docs/encirclement_sources.json').read_text());project=ROOT/'make_serbia_great_again'
 assert LIVE.resolve(strict=True)==LIVE.absolute()
 for name in ['phase1','kosovo','post_kosovo','bosnia','transition','post_bosnia']:
  r=json.loads((ROOT/f'docs/encirclement_regression_{name}.json').read_text());assert r.get('static_validation',r.get('static_and_model_validation'))=='passed' and Path(r['validated_mod_root'])==LIVE
 r=json.loads((ROOT/'docs/encirclement_validation.json').read_text());assert r['static_and_model_validation']=='passed' and Path(r['validated_mod_root'])==LIVE
 before=inventory(project);actual=inventory(LIVE)
 changed=sorted(p for p in actual if before.get(p)!=actual[p]);assert set(changed)<=set(sources['changed_relative_paths'])
 for p in changed:
  destination=project/p;assert destination.resolve().is_relative_to(project)
  destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(LIVE/p,destination)
 assert inventory(project)==actual
 launcher=LIVE.parent/'make_serbia_great_again.mod';assert launcher.read_bytes()==(project/'make_serbia_great_again.mod').read_bytes()
 for d in [launcher,LIVE/'make_serbia_great_again.mod']:
  declared=re.search(r'^path="([^"]+)"',d.read_text(),re.M)[1];assert Path(declared).resolve()==LIVE
 report={'version':'0.11.0','direction':'runtime_to_project','runtime':str(LIVE),'source':str(project),'matching_file_count':len(actual),'identical':True,'launcher_descriptor_matches':True,'changed_files':sources['changed_relative_paths'],'latest_synced_files':changed,'sha256':actual,'gameplay_validation':'pending user; game was not automated'}
 (ROOT/'docs/encirclement_sync.json').write_text(json.dumps(report,indent=2)+'\n');print(f'{len(actual)} source/runtime files identical; {len(changed)} synchronized from validated live installation; descriptor verified.')
if __name__=='__main__':main()
