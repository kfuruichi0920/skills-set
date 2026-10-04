"""Verify staged bytes retain the hashes used for source and visual review."""
import hashlib
import json
import subprocess
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
REPO=BASE.parents[2]


def verify(path,expected):
    relative=path.relative_to(REPO).as_posix()
    data=subprocess.check_output(['git','show',':'+relative],cwd=REPO)
    assert hashlib.sha256(data).hexdigest()==expected,relative


if __name__=='__main__':
    entries=json.loads((BASE/'catalog/diagram-vocabulary.json').read_text(encoding='utf-8'))['entries']
    for entry in entries:
        path=REPO/entry['artifact'];verify(path,entry['artifact_hash']);verify(path.with_name('preview.png'),entry['preview_hash'])
        if entry.get('external_source'):
            source=entry['external_source'];verify(path.parent/source['render'],source['sha256'])
        if entry.get('source_preservation'):
            source=entry['source_preservation'];verify(path.parent/source['path'],source['sha256'])
    for asset in json.loads((BASE/'sources/official-assets.json').read_text(encoding='utf-8'))['assets']:
        verify(BASE/'sources'/asset['local_path'],asset['sha256'])
    source=json.loads((BASE/'sources/user-input.json').read_text(encoding='utf-8'))
    verify(BASE/'sources'/source['source'],source['sha256'])
    print('Verified staged sample, preview, external source, official asset and input bytes')
