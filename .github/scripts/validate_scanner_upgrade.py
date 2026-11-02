"""One reviewed scanner-authority transition; ordinary PRs remain frozen."""
import hashlib, json, os, subprocess

REPOSITORY = 'appolon1908/Mobile-Control-Console'
BASE = '0610b673057de16674becbffa58c6b8dd428801d'
EXPECTED = {'.github/scripts/validate_source_scope.py': 'e8a6a0038ec72677464ae8bc49be001a6d32c225248173e12e2b072a34f6ed76', '.github/source-scope.json': 'c5c783de8f87237a4117dd4484c62b9029d73699222b939a4dcc4f72b6ad4198', 'governance/interim-release-policy.json': '94ece4d91faf0f2d4e48f367a85d44ce41045dd6d68e7c5337f25e88ff609454', '.github/scripts/test_source_scope.py': '19219d4715baaa55150ffa279bef50c1d16895aa7e5103f7d7853cebc9ae3f7f', '.github/scripts/test_secret_scanner.sh': '4d783f4f8ea40ec7acdbb94c4732f0ec2f9b320cea1e6a408a6702f08ee2d016'}
OLD_CONTEXT = 'documentation-contract-source'
NEW_CONTEXT = 'documentation-contract-source-v2'
EXTERNAL_REVIEW_FILES = {'.github/workflows/source-scope.yml', '.github/scripts/validate_scanner_upgrade.py'}

def trusted_manifest(base, repository):
    if base != BASE or repository != REPOSITORY:
        raise ValueError('Unregistered scanner authority transition')
    changes = subprocess.check_output(['git', 'diff', '--raw', '--no-abbrev', '--no-renames', base, 'HEAD']).decode().splitlines()
    changed = set()
    for entry in changes:
        metadata, path = entry.split('\t', 1)
        old_mode, new_mode, old_blob, new_blob, status = metadata[1:].split()
        if path not in set(EXPECTED) | EXTERNAL_REVIEW_FILES or new_mode != '100644' or status not in ('A', 'M'):
            raise ValueError('Unreviewed source, authority, mode or path change: ' + path)
        changed.add(path)
        if path in EXPECTED:
            content = subprocess.check_output(['git', 'show', 'HEAD:' + path])
            if hashlib.sha256(content).hexdigest() != EXPECTED[path]:
                raise ValueError('Reviewed scanner delta changed: ' + path)
    if changed != set(EXPECTED) | EXTERNAL_REVIEW_FILES:
        raise ValueError('Scanner upgrade delta incomplete')
    if subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal']).strip():
        raise ValueError('Dirty or untracked scanner upgrade source')
    manifest = json.loads(subprocess.check_output(['git', 'show', base + ':.github/source-scope.json']))
    policy = manifest['structured_files']['governance/interim-release-policy.json']
    found = 0
    for check in policy['required_checks']:
        if check['context'] == OLD_CONTEXT:
            check['context'] = NEW_CONTEXT
            found += 1
    if found != 1:
        raise ValueError('Unexpected prior scope policy')
    return manifest

if __name__ == '__main__':
    trusted_manifest(os.environ['BASE_SHA'], os.environ['GITHUB_REPOSITORY'])
    print('Exact reviewed scanner-only authority transition PASS; product source unchanged')
