# ScyllaDB Alternator Table Backup Tool

## Overview

This Python script is a **production-ready backup tool** for ScyllaDB Alternator tables. It creates snapshot-based backups with schema files, providing a complete solution for backing up DynamoDB-compatible tables running on ScyllaDB. The tool intelligently separates table schemas from materialized views for proper restoration.

## Features

✅ **Interactive Menu** - User-friendly command-line interface  
✅ **Single Table Backup** - Backup specific tables on demand  
✅ **Batch Backup** - Backup all tables with one command  
✅ **Schema Export** - Exports table DDL and materialized views to separate CQL files  
✅ **Materialized Views Handling** - Automatically separates and saves materialized views  
✅ **Snapshot-Based** - Uses ScyllaDB's native snapshot feature  
✅ **Compressed Archives** - Creates `.tar.gz` files for easy storage/transfer  
✅ **Comprehensive Logging** - Logs to both file and console  
✅ **Error Handling** - Graceful error handling with detailed messages  
✅ **Progress Tracking** - Shows success/failure statistics  
✅ **Python 3.6+ Compatible** - Works with Python 3.6.8 and above  

## Prerequisites

- Python 3.6+
- boto3 library
- ScyllaDB with Alternator enabled
- cqlsh command-line tool
- nodetool command-line tool
- Access to ScyllaDB data directory (`/var/lib/scylla/data`)

## Installation

```bash
# Install required package
pip install boto3

# Verify cqlsh is available
cqlsh --version

# Verify nodetool is available
nodetool version
```

## Configuration

The script connects to a local ScyllaDB Alternator instance. Update these settings if needed:

```python
ENDPOINT = "http://localhost:8000"      # Alternator endpoint
DATA_DIR = "/var/lib/scylla/data"       # ScyllaDB data directory
REGION = "us-east-1"                     # Required by boto3 (ignored by ScyllaDB)
AWS_ACCESS_KEY_ID = 'cassandra'          # ScyllaDB username
AWS_SECRET_ACCESS_KEY = '<password>'     # ScyllaDB salted_hash
USER = 'cassandra'                       # CQL username
PASSWORD = 'cassandra'                   # CQL password
```

AWS_SECRET_ACCESS_KEY is a salted hash for the user(cassandra):

```cql
cassandra@cqlsh:newdb> use system_auth;
cassandra@cqlsh:system_auth> describe tables;

role_permissions  role_attributes  role_members  roles

cassandra@cqlsh> use system_auth;
cassandra@cqlsh:system_auth> select * from roles;

 role      | can_login | is_superuser | member_of | salted_hash
-----------+-----------+--------------+-----------+------------------------------------------------------------------------------------------------------------
 cassandra |      True |         True |      null | $6$Wss/K5OMZ4tbUfRh$ZpF4Z4TW9N4xUTCa41QFcyV0pSW3wTbCNOrZIMbsgPhkz6wxI4EJ1mZYB/52IUZsNjTuvFQ0qWjw.xLLYvjox1

(1 rows)
```

## Usage

### Basic Usage

```bash
# Run the script
python3 baskup.py
```

### Interactive Menu

```txt
============================================================
ScyllaDB Alternator Table Backup Tool
============================================================

Fetching list of all available tables...

Available tables (3 total):
  1. users
  2. orders
  3. products

Options:
1. Backup a specific table
2. Backup all tables
3. Exit

Enter your choice (1, 2, or 3):
```

## Menu Options

### Option 1: Backup a Specific Table

Select this option to backup a single table.

**Example:**
```
Enter your choice (1, 2, or 3): 1
Enter table name: users

2024-12-10 10:30:15 - INFO - ===== Start backup process for users =====
2024-12-10 10:30:15 - INFO - Table ID for users: 220f8fd0aca211f0af61efb5703633f5
2024-12-10 10:30:16 - INFO - Creating schema file for users at ./backups/users/table_schema.cql
2024-12-10 10:30:16 - INFO - Successfully retrieved DESC TABLE output (1234 characters)
2024-12-10 10:30:16 - INFO - ✓ Table schema extracted: 850 characters
2024-12-10 10:30:16 - INFO - ✓ Materialized views found: 2
2024-12-10 10:30:16 - INFO - ✓ Table schema saved to: ./backups/users/table_schema.cql
2024-12-10 10:30:16 - INFO - ✓ Materialized view 1 saved to: ./backups/users/materialized_view_1.cql
2024-12-10 10:30:16 - INFO - ✓ Materialized view 2 saved to: ./backups/users/materialized_view_2.cql
2024-12-10 10:30:17 - INFO - Taking snapshot for alternator_users
2024-12-10 10:30:18 - INFO - Snapshot created for users with ID: 1733313018
2024-12-10 10:30:18 - INFO - Snapshot directory verified: /var/lib/scylla/data/alternator_users/users-220f8fd0aca211f0af61efb5703633f5/snapshots/1733313018/
2024-12-10 10:30:19 - INFO - Creating backup archive: ./backups/users/users_backup.tar.gz
2024-12-10 10:30:20 - INFO - Backup created at ./backups/users/users_backup.tar.gz
2024-12-10 10:30:20 - INFO - ===== Backup completed for users =====

✅ Backup completed successfully for users
```

**Output Files:**
```
./backups/users/
├── table_schema.cql            # Base table schema (DDL)
├── materialized_view_1.cql     # First materialized view
├── materialized_view_2.cql     # Second materialized view
└── users_backup.tar.gz         # Compressed snapshot data
```

### Option 2: Backup All Tables

Select this option to backup all tables in the database.

**Example:**
```
Enter your choice (1, 2, or 3): 2

Backing up 3 tables...

2024-12-10 10:35:00 - INFO - ===== Start backup process for users =====
...
2024-12-10 10:35:05 - INFO - ===== Backup completed for users =====

2024-12-10 10:35:05 - INFO - ===== Start backup process for orders =====
...
2024-12-10 10:35:10 - INFO - ===== Backup completed for orders =====

2024-12-10 10:35:10 - INFO - ===== Start backup process for products =====
...
2024-12-10 10:35:15 - INFO - ===== Backup completed for products =====

============================================================
Backup Summary:
  ✅ Successful: 3
  ❌ Failed: 0
  📊 Total: 3
============================================================
```

**If some tables fail:**
```
============================================================
Backup Summary:
  ✅ Successful: 2
  ❌ Failed: 1
  📊 Total: 3

Failed tables:
  - orders
============================================================
```

### Option 3: Exit

Exits the script gracefully.

## Backup Process Flow

The script follows a 5-step backup process for each table:

### Step 1: Get Table ID
Retrieves the internal UUID that ScyllaDB uses to identify the table.

```python
TABLE_ID = get_table_id(table_name)
# Returns: "220f8fd0aca211f0af61efb5703633f5"
```

**Why needed:** ScyllaDB stores table data in directories named with UUIDs:
```
/var/lib/scylla/data/alternator_users/users-220f8fd0aca211f0af61efb5703633f5/
```

### Step 2: Create Schema Files
Exports the table schema (DDL) and separates materialized views into individual CQL files.

```python
create_schema_file(table_name)
# Creates: ./backups/users/table_schema.cql
# Creates: ./backups/users/materialized_view_1.cql (if exists)
# Creates: ./backups/users/materialized_view_2.cql (if exists)
```

**Base table schema file (table_schema.cql):**
```sql
CREATE TABLE alternator_users.users (
    pk text,
    sk text,
    age int,
    name text,
    email text,
    data text,
    PRIMARY KEY (pk, sk)
) WITH ...;
```

**Materialized view files (materialized_view_1.cql, etc.):**
```sql
CREATE MATERIALIZED VIEW alternator_users.users_by_age AS
    SELECT pk, sk, age, name
    FROM alternator_users.users
    WHERE age IS NOT NULL AND pk IS NOT NULL AND sk IS NOT NULL
    PRIMARY KEY (age, pk, sk)
    WITH ...;
```

**Schema Separation Benefits:**
- ✅ Proper restoration order (table first, then views)
- ✅ Independent view management
- ✅ Clear visibility of table structure
- ✅ Easier troubleshooting

### Step 3: Take Snapshot
Creates a point-in-time snapshot of the table's SSTable files.

```python
snapshot_id = take_snapshot(table_name)
# Returns: "1733313018" (Unix timestamp)
```

**What's created:**
```
/var/lib/scylla/data/alternator_users/users-220f8fd0aca211f0af61efb5703633f5/snapshots/1733313018/
├── mc-1-big-Data.db
├── mc-1-big-Index.db
├── mc-1-big-Summary.db
├── mc-1-big-Statistics.db
└── mc-1-big-TOC.txt
```

### Step 4: Verify Snapshot Directory
Ensures the snapshot was actually created on disk.

```python
if not os.path.exists(snapshot_dir):
    return False
```

### Step 5: Create Backup Archive
Compresses the snapshot into a portable tar.gz file.

```python
tar_cmd = ["tar", "czf", backup_file, "-C", snapshot_dir, "."]
# Creates: ./backups/users/users_backup.tar.gz
```

## Output Structure

After running backups, your directory structure will look like:

```
./backups/
├── users/
│   ├── table_schema.cql
│   ├── materialized_view_1.cql
│   ├── materialized_view_2.cql
│   └── users_backup.tar.gz
├── orders/
│   ├── table_schema.cql
│   └── orders_backup.tar.gz
└── products/
    ├── table_schema.cql
    ├── materialized_view_1.cql
    └── products_backup.tar.gz
```

## Logging

The script logs to both file and console:

### Log File
- **Location:** `./alternator_backup.log`
- **Format:** `2024-12-10 10:30:15 - INFO - Message`
- **Retention:** Append mode (keeps all logs)

### Console Output
- Real-time progress updates
- Success/failure indicators (✅/❌)
- Summary statistics
- Schema extraction details

### Log Levels

| Level | Description | Example |
|-------|-------------|---------|
| INFO | Normal operations | `✓ Table schema extracted: 850 characters` |
| WARNING | Non-critical issues | `No tables found in database` |
| ERROR | Operation failures | `✗ Failed to extract table schema` |
| EXCEPTION | Unexpected errors | `Unexpected error during backup` |

## Error Handling

### Fail-Fast Strategy

The script uses a **fail-fast** approach for single table backups:

```python
if not TABLE_ID:
    return False  # Stop immediately

if not create_schema_file(table_name):
    return False  # Stop immediately

if not snapshot_id:
    return False  # Stop immediately
```

If any step fails, the backup stops and returns `False`.

### Batch Backup Resilience

For batch backups (Option 2), the script:
- ✅ Continues even if one table fails
- ✅ Tracks failed tables
- ✅ Shows summary at the end
- ✅ Logs all errors for troubleshooting

### Common Error Scenarios

#### 1. Table Not Found
```
❌ Table 'invalid_table' not found.
```
**Solution:** Check table name spelling or list available tables.

#### 2. Permission Denied
```
ERROR - Failed to create backup folder ./backups/users/: Permission denied
```
**Solution:** Run with appropriate permissions or change backup directory.

#### 3. Snapshot Failed
```
ERROR - Snapshot command failed: Error: Keyspace alternator_users does not exist
```
**Solution:** Verify table exists and Alternator is running.

#### 4. Schema Extraction Failed
```
ERROR - ✗ Failed to extract table schema
```
**Solution:** Check cqlsh connection and user permissions.

#### 5. Disk Space
```
ERROR - Failed to create backup archive: No space left on device
```
**Solution:** Free up disk space or change backup location.

## Keyboard Interrupt Handling

Press **Ctrl+C** to gracefully interrupt the backup process:

```
^C
Backup process interrupted by user.
```

**Exit code:** 130 (standard for keyboard interrupt)

## Function Reference

### `get_table_id(table_name)`
**Purpose:** Get the internal UUID for a table.

**Parameters:**
- `table_name` (str): Name of the table

**Returns:** 
- `str`: Table UUID without dashes
- `None`: If table not found or error occurs

**Example:**
```python
table_id = get_table_id("users")
# Returns: "220f8fd0aca211f0af61efb5703633f5"
```

---

### `separate_schema_and_views(desc_output)`
**Purpose:** Parse DESC TABLE output and separate base table schema from materialized views.

**Parameters:**
- `desc_output` (str): The full output string from DESC TABLE command

**Returns:** 
- `tuple`: (create_table_str, list_of_materialized_view_str)

**Example:**
```python
table_schema, materialized_views = separate_schema_and_views(desc_output)
# Returns: ("CREATE TABLE ...", ["CREATE MATERIALIZED VIEW ...", "CREATE MATERIALIZED VIEW ..."])
```

**Algorithm:**
- Uses regex to find `CREATE TABLE` statements ending with semicolon
- Uses regex to find all `CREATE MATERIALIZED VIEW` statements
- Handles cases where semicolons may or may not be present
- Normalizes line endings for cross-platform compatibility

---

### `create_schema_file(table_name)`
**Purpose:** Export table schema and materialized views to separate CQL files.

**Parameters:**
- `table_name` (str): Name of the table

**Returns:** 
- `True`: Schema files created successfully
- `None`: Error occurred

**Output Files:**
- `./backups/{table_name}/table_schema.cql` - Base table DDL
- `./backups/{table_name}/materialized_view_N.cql` - Each materialized view

**Features:**
- Automatically creates backup folder if it doesn't exist
- Separates table schema from materialized views
- Adds semicolons to view statements if missing
- Logs extraction statistics (character count, number of views)

---

### `take_snapshot(table_name)`
**Purpose:** Create a snapshot of table data.

**Parameters:**
- `table_name` (str): Name of the table

**Returns:** 
- `str`: Snapshot ID (Unix timestamp)
- `None`: Snapshot failed

**Example:**
```python
snapshot_id = take_snapshot("users")
# Returns: "1733313018"
```

---

### `get_all_tables()`
**Purpose:** List all available tables.

**Parameters:** None

**Returns:** 
- `list`: List of table names
- `[]`: Empty list if no tables or error

**Example:**
```python
tables = get_all_tables()
# Returns: ['users', 'orders', 'products']
```

---

### `backup_table(table_name)`
**Purpose:** Complete backup process for a single table.

**Parameters:**
- `table_name` (str): Name of the table

**Returns:** 
- `True`: Backup completed successfully
- `False`: Backup failed

**Side Effects:**
- Creates `./backups/{table_name}/` directory
- Creates `table_schema.cql` file
- Creates `materialized_view_N.cql` files (if views exist)
- Creates `{table_name}_backup.tar.gz` archive
- Writes logs to `alternator_backup.log`

---

## Restoration Process

To restore a backup:

### Step 1: Restore Base Table Schema

```bash
# Extract table name from schema file
TABLE_NAME="users"

# Apply base table schema first
cqlsh -u cassandra -p cassandra -f ./backups/$TABLE_NAME/table_schema.cql
```

### Step 2: Restore Materialized Views

**Important:** Restore views AFTER the base table is created and populated.

```bash
# Apply each materialized view in sequence
cqlsh -u cassandra -p cassandra -f ./backups/$TABLE_NAME/materialized_view_1.cql
cqlsh -u cassandra -p cassandra -f ./backups/$TABLE_NAME/materialized_view_2.cql
```

**Why separate restoration?**
- Materialized views depend on the base table existing
- Views are populated automatically from base table data
- Restoring views before data can cause errors

### Step 3: Restore Data

```bash
# Extract backup archive
mkdir -p /tmp/restore_$TABLE_NAME
tar xzf ./backups/$TABLE_NAME/${TABLE_NAME}_backup.tar.gz -C /tmp/restore_$TABLE_NAME/

# Get table ID (you'll need to find this from the restored table)
TABLE_ID=$(cqlsh -u cassandra -p cassandra -e "SELECT id FROM system_schema.tables WHERE keyspace_name = 'alternator_$TABLE_NAME' AND table_name = '$TABLE_NAME';" | grep -oP '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | tr -d '-')

# Stop ScyllaDB
sudo systemctl stop scylla-server

# Copy files to ScyllaDB data directory
RESTORE_DIR="/var/lib/scylla/data/alternator_$TABLE_NAME/${TABLE_NAME}-$TABLE_ID"
sudo cp /tmp/restore_$TABLE_NAME/* $RESTORE_DIR/

# Fix permissions
sudo chown -R scylla:scylla $RESTORE_DIR

# Start ScyllaDB
sudo systemctl start scylla-server

# Refresh table
nodetool refresh alternator_$TABLE_NAME $TABLE_NAME
```

### Step 4: Verify Restoration

```bash
# Check table data
cqlsh -u cassandra -p cassandra -e "SELECT COUNT(*) FROM alternator_$TABLE_NAME.$TABLE_NAME;"

# Check materialized views
cqlsh -u cassandra -p cassandra -e "SELECT COUNT(*) FROM alternator_$TABLE_NAME.users_by_age;"
```

## Troubleshooting

### Issue: No tables found

**Symptoms:**
```
No tables found.
```

**Diagnosis:**
```bash
# Check if Alternator is running
curl http://localhost:8000

# Check if tables exist in ScyllaDB
cqlsh -u cassandra -p cassandra -e "SELECT keyspace_name FROM system_schema.keyspaces WHERE keyspace_name LIKE 'alternator_%';"
```

**Solution:**
1. Verify Alternator is enabled in `scylla.yaml`
2. Restart ScyllaDB: `sudo systemctl restart scylla-server`
3. Create test table if needed

---

### Issue: Permission denied creating backup folder

**Symptoms:**
```
ERROR - Failed to create backup folder ./backups/users/: Permission denied
```

**Solution:**
```bash
# Option 1: Run with sudo
sudo python3 baskup.py

# Option 2: Change ownership
sudo chown -R $USER:$USER ./backups/

# Option 3: Use different directory
# Edit script: BACKUP_FOLDER = "/tmp/backups/{table_name}"
```

---

### Issue: Snapshot directory not found

**Symptoms:**
```
ERROR - Snapshot directory /var/lib/scylla/data/.../snapshots/1733313018/ does not exist
```

**Diagnosis:**
```bash
# Check if snapshot was created
nodetool listsnapshots

# Check data directory permissions
ls -la /var/lib/scylla/data/
```

**Solution:**
1. Verify nodetool is working: `nodetool status`
2. Check ScyllaDB is running: `systemctl status scylla-server`
3. Review ScyllaDB logs: `journalctl -u scylla-server -n 100`

---

### Issue: Failed to extract table schema

**Symptoms:**
```
ERROR - ✗ Failed to extract table schema
```

**Diagnosis:**
```bash
# Test DESC TABLE manually
cqlsh -u cassandra -p cassandra -e "DESC TABLE alternator_users.users;"
```

**Solution:**
1. Verify table exists in keyspace
2. Check user has SELECT permissions on system_schema
3. Review DESC TABLE output format

---

## Security Considerations

⚠️ **Warning:** This script contains hardcoded credentials suitable only for local development and testing.

### For Production:

1. **Use Environment Variables**
```python
import os
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
```

2. **Use IAM Roles** (when running on AWS)

3. **Secure Backup Files**
```bash
# Encrypt backups
gpg --encrypt --recipient user@example.com users_backup.tar.gz

# Set restrictive permissions
chmod 600 ./backups/*/*.tar.gz
chmod 600 ./backups/*/*.cql
```

4. **Never Commit Credentials** to version control

## Performance Considerations

### Disk Space

Each backup requires space for:
- Snapshot (same size as table data)
- Compressed archive (~50-70% of snapshot size)
- Schema files (typically < 10 KB each)

**Example:**
- Table size: 1 GB
- Snapshot size: 1 GB
- Archive size: ~600 MB
- Schema files: ~5 KB each
- **Total needed:** ~1.6 GB

### Backup Time

Typical times (varies by hardware):
- Small table (< 100 MB): 5-10 seconds
- Medium table (1 GB): 30-60 seconds
- Large table (10 GB): 5-10 minutes

### Network Transfer

For remote backups, compress before transfer:
```bash
# Already compressed with tar czf
scp ./backups/users/users_backup.tar.gz remote-server:/backup/
scp ./backups/users/*.cql remote-server:/backup/schemas/
```

## Best Practices

### 1. Regular Backups
```bash
# Create cron job for daily backups
0 2 * * * /usr/bin/python3 /app/alternator/baskup.py <<< "2" >> /var/log/backup.log 2>&1
```

### 2. Retention Policy
```bash
# Keep last 7 days of backups
find ./backups/ -name "*.tar.gz" -mtime +7 -delete
find ./backups/ -name "*.cql" -mtime +7 -delete
```

### 3. Verify Backups
```bash
# Test extraction
tar tzf ./backups/users/users_backup.tar.gz | head

# Validate schema files
for schema in ./backups/users/*.cql; do
    echo "Checking $schema"
    grep -q "CREATE TABLE\|CREATE MATERIALIZED VIEW" "$schema" && echo "✓ Valid" || echo "✗ Invalid"
done
```

### 4. Off-site Storage
```bash
# Upload to S3
aws s3 sync ./backups/ s3://my-bucket/scylla-backups/

# Upload to remote server
rsync -av ./backups/ backup-server:/backups/scylla/
```

### 5. Document Restoration
Keep restoration instructions with backups:
```bash
cat > ./backups/users/README.txt << EOF
Restore date: $(date)
Table: users
Snapshot ID: 1733313018
Base table schema: table_schema.cql
Materialized views: $(ls -1 ./backups/users/materialized_view_*.cql 2>/dev/null | wc -l)

Restoration order:
1. Apply table_schema.cql
2. Restore data from users_backup.tar.gz
3. Apply materialized_view_*.cql files in sequence
EOF
```

## Important Notes

### ScyllaDB-Specific Metadata

The schema files may contain ScyllaDB-specific metadata:
```sql
WITH scylla_tags = {}
```

**Action Required:** This metadata is automatically handled by the script's parsing logic. However, if you manually edit schema files, ensure compatibility with your target CQL environment.

### Snapshot Persistence

- Snapshots persist until manually deleted
- Use `nodetool clearsnapshot` to remove old snapshots
- Monitor disk usage: `du -sh /var/lib/scylla/data/*/snapshots/`

### Materialized Views

- Views are separated into individual CQL files for clarity
- Views must be restored AFTER the base table
- Views will be automatically populated from base table data
- Each view file includes a semicolon for proper CQL execution

### Index Handling

- Indexes in the base table are included in `table_schema.cql`
- Indexes are NOT included in the snapshot data
- Indexes will be rebuilt automatically when restoring the schema

## Related Documentation

- [ScyllaDB Alternator Documentation](https://docs.scylladb.com/stable/using-scylla/alternator/)
- [ScyllaDB Backup and Restore](https://docs.scylladb.com/stable/operating-scylla/procedures/backup-restore/)
- [ScyllaDB Materialized Views](https://docs.scylladb.com/stable/cql/mv/)
- [Boto3 DynamoDB Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)
- [ScyllaDB Nodetool Reference](https://docs.scylladb.com/stable/operating-scylla/nodetool/)

## Version History

- **v1.1** - Current release
  - ✅ Separated materialized views from base table schema
  - ✅ Individual CQL files for each materialized view
  - ✅ Enhanced schema parsing with `separate_schema_and_views()`
  - ✅ Improved logging with extraction statistics
  - ✅ Better restoration workflow documentation

- **v1.0** - Initial release
  - Single table backup
  - Batch backup for all tables
  - Schema export
  - Snapshot-based backups
  - Compressed archives
  - Comprehensive error handling
  - Python 3.6+ compatible

## License

This script is provided as-is for educational and operational purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `alternator_backup.log`
3. Verify ScyllaDB and Alternator are running
4. Check ScyllaDB documentation
5. Validate schema file structure

---

**Note:** This tool is designed for production use with proper error handling, logging, and materialized view separation. Always test in a non-production environment first and verify backups can be restored successfully, paying special attention to the restoration order of base tables and their materialized views.
