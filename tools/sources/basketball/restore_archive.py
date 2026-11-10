"""Verify and restore the archived basketball inputs from a local ZIP.

Usage: python restore_archive.py ARCHIVE.zip DESTINATION
The manifest is committed; the bulky sources are stored outside Git. Obtain
the ZIP using the restricted handoff link recorded in archive-package.json.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def restore(archive_path, destination):
    here = Path(__file__).resolve().parent
    package = json.loads((here / 'archive-package.json').read_text())
    manifest = json.loads((here / 'archive-manifest.json').read_text())
    if hashlib.sha256(archive_path.read_bytes()).hexdigest() != package['sha256']:
        raise ValueError('Archive checksum differs from the reviewed package')
    destination = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for item in manifest['files']:
            target = (destination / item['path']).resolve()
            if not target.is_relative_to(destination):
                raise ValueError('Unsafe archive path')
            data = archive.read(item['path'])
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                raise ValueError('Source checksum mismatch: ' + item['path'])
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != item['sha256']:
                raise ValueError('Refusing to replace a different local file: ' + str(target))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    print(f'Verified and restored {len(manifest["files"])} files to {destination}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    restore(args.archive, args.destination)
