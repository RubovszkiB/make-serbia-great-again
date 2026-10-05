"""Deploy the project mod to the user's primary HOI4 installation and verify hashes.

Copies every changed/missing project file and the sibling launcher descriptor.
Does not delete runtime-only files; reports them for review instead.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'make_serbia_great_again'
TARGET = Path('C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again')
REPORT = ROOT / 'docs/local_deployment.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in root.rglob('*') if p.is_file()}


def main():
    source = SOURCE.resolve(strict=True)
    target = TARGET.resolve(strict=True)
    assert target == TARGET.absolute(), 'Runtime target must not redirect through a link'
    launcher = target.parent / 'make_serbia_great_again.mod'
    descriptor = source / 'make_serbia_great_again.mod'
    text = descriptor.read_text(encoding='utf-8-sig')
    declared = re.search(r'^path="([^"]+)"', text, re.M)[1]
    assert Path(declared).resolve() == target, 'Project descriptor points to a different installation'
    before = inventory(target)
    expected = inventory(source)
    installed_descriptor = launcher.read_text(encoding='utf-8-sig') if launcher.exists() else ''
    installed_identity = re.search(r'^remote_file_id="(\d+)"', installed_descriptor, re.M)
    if installed_identity:
        assert f'remote_file_id="{installed_identity[1]}"' in text, 'Preserve existing Workshop identity'
        assert f'remote_file_id="{installed_identity[1]}"' in (source/'descriptor.mod').read_text()
    copied = []
    for relative, sha in sorted(expected.items()):
        destination = target / relative
        assert destination.resolve().is_relative_to(target), relative
        if before.get(relative) != sha:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, destination)
            copied.append(str(destination))
    if not launcher.exists() or digest(launcher) != digest(descriptor):
        shutil.copyfile(descriptor, launcher)
        copied.append(str(launcher))
    actual = inventory(target)
    assert all(actual.get(name) == sha for name, sha in expected.items()), 'Runtime content differs'
    assert digest(launcher) == digest(descriptor), 'Launcher descriptor differs'
    focus = (target/'common/national_focus/MSGA_SER_phase1.txt').read_text(encoding='utf-8-sig')
    required = ['internal_investment_drive', 'settle_old_political_accounts',
                'secure_the_national_assembly', 'send_the_migrants_back',
                'serbia_stands_united', 'reconstitute_serbian_volunteer_guard']
    assert all(re.search(r'\bid\s*=\s*MSGA_'+name+r'\b', focus) for name in required)
    report = {
        'runtime_target': str(target), 'launcher_descriptor': str(launcher),
        'version': re.search(r'^version="([^"]+)"', text, re.M)[1],
        'before_missing_files': sorted(expected.keys() - before.keys()),
        'before_changed_files': sorted(n for n in expected.keys() & before.keys() if expected[n] != before[n]),
        'copied_absolute_paths': copied,
        'verified_source_file_count': len(expected),
        'verified_sha256_by_relative_path': expected,
        'runtime_only_files': sorted(actual.keys() - expected.keys()),
        'all_project_files_match_runtime': True,
        'launcher_descriptor_matches_project': True,
        'descriptor_path_verified': declared,
        'required_new_focuses_present': ['MSGA_' + n for n in required],
        'game_launched': False,
    }
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['runtime_target', 'version', 'verified_source_file_count',
          'runtime_only_files', 'all_project_files_match_runtime', 'launcher_descriptor_matches_project',
          'required_new_focuses_present']}, indent=2))
    print(f'Deployed {len(copied)} files; exact paths and hashes: {REPORT}')


if __name__ == '__main__':
    main()
