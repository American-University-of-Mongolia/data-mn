"""Upload a verified local basketball archive tree without changing bucket ACLs.

Requires boto3 and standard AWS credential configuration. Set --endpoint and
--bucket to an approved location if it differs from the documented server.
Writes a receipt only after every object's downloaded SHA-256 is verified.
"""
import argparse
import hashlib
import json
from pathlib import Path
import boto3


def upload(root, endpoint, bucket, receipt):
    manifest = json.loads((Path(__file__).parent / 'archive-manifest.json').read_text())
    client = boto3.client('s3', endpoint_url=endpoint)
    verified = []
    for item in manifest['files']:
        source = root / item['path']
        if hashlib.sha256(source.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Local source hash mismatch: ' + item['path'])
        key = item['object_key']
        try:
            existing = client.head_object(Bucket=bucket, Key=key)
        except client.exceptions.ClientError as error:
            if error.response['Error']['Code'] not in ('404', 'NoSuchKey', 'NotFound'):
                raise
            existing = None
        if existing and existing.get('Metadata', {}).get('sha256') != item['sha256']:
            raise ValueError('Refusing to overwrite a different object: ' + key)
        if not existing:
            client.upload_file(str(source), bucket, key, ExtraArgs={'Metadata': {'sha256': item['sha256']}})
        response = client.get_object(Bucket=bucket, Key=key)
        digest = hashlib.sha256()
        with response['Body'] as stream:
            for chunk in stream.iter_chunks(chunk_size=1024*1024):
                digest.update(chunk)
        if digest.hexdigest() != item['sha256']:
            raise ValueError('Uploaded object hash mismatch: ' + key)
        verified.append(key)
        print(f'{len(verified)} / {len(manifest["files"])} verified', flush=True)
    receipt.write_text(json.dumps({'endpoint': endpoint, 'bucket': bucket, 'verified_objects': verified}, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_root', type=Path)
    parser.add_argument('--endpoint', default='https://s3.data.mn')
    parser.add_argument('--bucket', default='data.mn')
    parser.add_argument('--receipt', type=Path, default=Path('basketball-upload-receipt.json'))
    args = parser.parse_args()
    upload(args.source_root, args.endpoint, args.bucket, args.receipt)
