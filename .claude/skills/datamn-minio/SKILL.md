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

- **Type:** Bare metal (not Docker)
- **Binary:** `/usr/local/bin/minio`
- **Data directory:** `/home/ritz/lexica/minio/data`
- **Config directory:** `/home/ritz/lexica/minio/`
- **Environment file:** `/home/ritz/lexica/minio/.env`

## Service Configuration

MinIO runs as a user systemd service:

```
~/.config/systemd/user/minio.service
```

Service binds to localhost only:
- API: 127.0.0.1:9000
- Console: 127.0.0.1:9001

### Managing the Service

```bash
# Check status
ssh lexica "systemctl --user status minio"

# Restart
ssh lexica "systemctl --user restart minio"

# View logs
ssh lexica "journalctl --user -u minio -f"
```

## Public Access

nginx reverse proxy exposes MinIO publicly:

| Service | URL |
|---------|-----|
| S3 API | https://s3.data.mn |
| Console | https://console.s3.data.mn |

**Nginx config:** `/etc/nginx/conf.d/minio.conf`
**SSL certs:** `/etc/letsencrypt/live/s3.data.mn/`

## Credentials

```
Username: ritz
Password: jYb00u3BFaC69qBNAmsoYirgrahdkVaK
```

## Bucket Structure

Single bucket: `data.mn`

| Folder | Size | Contents |
|--------|------|----------|
| unegui/ | ~144MB | Real estate listings (CSV) |
| agaar/ | ~372K | Air quality data (Parquet) |
| weather/ | ~256K | Ulaanbaatar weather (Parquet) |
| traffic/ | ~184K | Ulaanbaatar traffic (Parquet) |

### Files

**unegui/**
- unegui_apartments.csv
- unegui_apartments_rent.csv
- unegui_cars.csv
- unegui_cars_old.csv
- unegui_offices_rent.csv
- unegui_offices_sale.csv

**agaar/**
- agaar_air_quality.parquet

**weather/**
- ulaanbaatar_weather.parquet

**traffic/**
- ulaanbaatar_traffic.parquet

## Using with Python (boto3)

```python
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='https://s3.data.mn',
    aws_access_key_id='ritz',
    aws_secret_access_key='jYb00u3BFaC69qBNAmsoYirgrahdkVaK'
)

# List objects
response = s3.list_objects_v2(Bucket='data.mn')
for obj in response.get('Contents', []):
    print(obj['Key'])

# Download file
s3.download_file('data.mn', 'unegui/unegui_apartments.csv', 'local_file.csv')

# Upload file
s3.upload_file('local_file.csv', 'data.mn', 'path/in/bucket.csv')
```

## Using with mc (MinIO Client)

```bash
# Configure alias
mc alias set datamn https://s3.data.mn ritz jYb00u3BFaC69qBNAmsoYirgrahdkVaK

# List buckets
mc ls datamn

# List files
mc ls datamn/data.mn/unegui/

# Copy file
mc cp datamn/data.mn/unegui/unegui_apartments.csv ./
```

## Related Services on lexica

- **JupyterLab:** jupyter.lexica.news (systemd: jupyter.service)
- **Lexica Search API:** lexica-search.service
- **nginx:** Reverse proxy for all services

## File Locations Summary

| File | Purpose |
|------|---------|
| `/usr/local/bin/minio` | MinIO binary |
| `/home/ritz/lexica/minio/.env` | Credentials |
| `/home/ritz/lexica/minio/data/` | Data storage |
| `~/.config/systemd/user/minio.service` | Service definition |
| `/etc/nginx/conf.d/minio.conf` | nginx proxy config |
| `/etc/letsencrypt/live/s3.data.mn/` | SSL certificates |
