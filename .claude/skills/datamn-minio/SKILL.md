---
name: datamn-minio
description: "Operate and consume the data.mn MinIO/S3 storage service on lexica. Use for bucket inspection, upload/download workflows, and service health checks without exposing plaintext credentials."
---


# MinIO S3 Server for data.mn

S3-compatible object storage for data.mn datasets, hosted on the lexica server.

## Server Location

| Property | Value |
|----------|-------|
| Hostname | lexica |
| Public IP | 103.119.92.177 |
| Local IP | 192.168.100.8 |
| SSH access | `ssh lexica` (local network only) |

## MinIO Installation

- Type: bare metal (not Docker)
- Binary: `/usr/local/bin/minio`
- Data directory: `/home/ritz/lexica/minio/data`
- Config directory: `/home/ritz/lexica/minio/`
- Environment file: `/home/ritz/lexica/minio/.env`

## Service Management

```bash
ssh lexica "systemctl --user status minio"
ssh lexica "systemctl --user restart minio"
ssh lexica "journalctl --user -u minio -f"
```

## Public Endpoints

| Service | URL |
|---------|-----|
| S3 API | https://s3.data.mn |
| Console | https://console.s3.data.mn |

## Credentials Policy

Do not store credentials in plaintext files or command history.

Preferred pattern:

1. Keep credentials in an age-encrypted file (for example `secrets.age`) in this skill directory.
2. Decrypt only when needed via the `age-encryption` skill workflow.
3. Export env vars at runtime and avoid hardcoding keys in scripts or code snippets.

Expected env vars:

- `DATAMN_S3_ENDPOINT`
- `DATAMN_S3_ACCESS_KEY`
- `DATAMN_S3_SECRET_KEY`

## Bucket

Primary bucket: `data.mn`

## Python (boto3)

```python
import os
import boto3

s3 = boto3.client(
    's3',
    endpoint_url=os.environ['DATAMN_S3_ENDPOINT'],
    aws_access_key_id=os.environ['DATAMN_S3_ACCESS_KEY'],
    aws_secret_access_key=os.environ['DATAMN_S3_SECRET_KEY'],
)

response = s3.list_objects_v2(Bucket='data.mn')
for obj in response.get('Contents', []):
    print(obj['Key'])
```

## MinIO Client (mc)

```bash
mc alias set datamn "$DATAMN_S3_ENDPOINT" "$DATAMN_S3_ACCESS_KEY" "$DATAMN_S3_SECRET_KEY"
mc ls datamn
mc ls datamn/data.mn/
```
