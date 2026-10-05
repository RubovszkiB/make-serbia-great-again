"""Sync the validated 0.12 live increment back to source and verify every hash."""
from pathlib import Path
import hashlib,json,re,shutil
from implement_pact_war import ROOT,LIVE

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(root):return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file()}

def main():
 assert LIVE.resolve(strict=True)==LIVE.absolute()
 sources=json.loads((ROOT/'docs/pact_war_sources.json').read_text())
 reports=['pact_war_regression_'+name+'.json' for name in ['phase1','kosovo','post_kosovo','bosnia','transition','post_bosnia','encirclement']]+['pact_war_validation.json']
 for name in reports:
  report=json.loads((ROOT/'docs'/name).read_text());assert report['validated_mod_root']==str(LIVE)
  assert any(report.get(k)=='passed' for k in ('validation','static_validation','static_and_model_validation')),name
 expected=set(sources['baseline_sha256'])|set(sources['changed_relative_paths'])
 current=inventory(LIVE);assert set(current)==expected,'Unexpected runtime files'
 for path,digest in sources['baseline_sha256'].items():
  if path not in sources['changed_relative_paths']:assert current[path]==digest,path
 source=ROOT/'make_serbia_great_again'
 existing=inventory(source)
 prior_path=ROOT/'docs/pact_war_sync.json'
 prior=json.loads(prior_path.read_text())['sha256'] if prior_path.exists() else {}
 assert set(existing)<=expected,'Unexpected repository mod files'
 for path,digest in existing.items():
  assert digest in {sources['baseline_sha256'].get(path),prior.get(path),current[path]},f'Unrelated source edit: {path}'
 for path in sources['changed_relative_paths']:
  target=source/path;assert target.resolve().is_relative_to(source)
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(LIVE/path,target)
 assert inventory(source)==current,'Source/live mismatch'
 descriptor=(LIVE/'make_serbia_great_again.mod').read_text();launcher=LIVE.parent/'make_serbia_great_again.mod'
 assert re.search(r'^path="([^"]+)"',descriptor,re.M)[1]==LIVE.as_posix()
 assert 'remote_file_id="3813570241"' in descriptor and 'remote_file_id="3813570241"' in (LIVE/'descriptor.mod').read_text()
 assert sha(launcher)==sha(source/'make_serbia_great_again.mod')
 report={'version':'0.12.0','runtime':str(LIVE),'source':str(source),'file_count':len(current),'changed_relative_paths':sources['changed_relative_paths'],'deployed_absolute_paths':sources['deployed_absolute_paths'],'sha256':current,'all_source_runtime_hashes_equal':True,'launcher_descriptor_path_and_hash_verified':True,'validation_reports':reports,'gameplay_validation':'Pending user; no active game window accessed'}
 (ROOT/'docs/pact_war_sync.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f'Synced validated LIVE files to source. All {len(current)} files and launcher match.')

if __name__=='__main__':main()
