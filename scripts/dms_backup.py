import os, tarfile, datetime, subprocess

timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = os.path.expanduser('~/genesis_node_00/backups')
target_dir = os.path.expanduser('~/genesis_node_00')
archive_file = os.path.join(backup_dir, f'genesis_snapshot_{timestamp}.tar.gz')

print(f'[GENESIS-DMS] Creating State Snapshot at {timestamp}...')
os.makedirs(backup_dir, exist_ok=True)

with tarfile.open(archive_file, 'w:gz') as tar:
    for root, dirs, files in os.walk(target_dir):
        if 'venv' in root or 'backups' in root:
            continue
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, target_dir)
            tar.add(full_path, arcname=rel_path)

if os.path.exists(archive_file):
    print(f'[GENESIS-DMS] SUCCESS: Compressed snapshot saved to {archive_file}')
