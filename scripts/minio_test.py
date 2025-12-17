# -----------------------------------------------------------
# minio_test.py
# -----------------------------------------------------------
# Quick test to validate MinIO setup
# -----------------------------------------------------------

from lake.minio_client import MinIOClient
import polars as pl

print("\nVERIFYING MINIO...\n")

client = MinIOClient()
print(f'✓ Connected to MinIO at {client.endpoint}')
print(f'✓ Using bucket: {client.bucket_name}')

# Quick test
test_df = pl.DataFrame({'test': [1, 2, 3]})
client.write_parquet(test_df, 'test/test.parquet')
result_df = client.read_parquet('test/test.parquet')
print(f'✓ Test passed: {len(result_df)} rows')
print()
# client.delete('test/test.parquet')
