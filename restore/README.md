# ScyllaDB Alternator Table Restore Tool

This script provides a complete restoration solution for ScyllaDB Alternator tables backed up using the baskup.py script.

## Restoration Process

A companion script `restore.py` is provided for restoring backups. This section documents the complete restoration workflow.

### Restoration Overview

The restore script (`restore.py`) provides:

✅ **Complete restoration** - Schema + Data + Materialized Views  
✅ **Safe operation** - Confirmation prompts for destructive actions  
✅ **Flexible restoration** - Single table or batch mode  
✅ **Backward compatibility** - Supports legacy and separated schema formats  
✅ **Proper ordering** - Base table → Data → Views  
✅ **Error resilience** - Continues batch restore if one table fails  
✅ **Comprehensive logging** - File + Console output  
✅ **Best practices** - Follows ScyllaDB restoration guidelines  

### Prerequisites for Restoration

- Root or sudo access (required for systemctl and file operations)
- ScyllaDB service installed and configured
- Backup files created by `baskup.py`
- cqlsh command-line tool
- nodetool command-line tool
- Access to ScyllaDB data directory (`/var/lib/scylla/data`)

### Running the Restore Tool

```bash
# Run with sudo (required for service control and file operations)
sudo python3 restore.py
```

### Interactive Restore Menu

```
============================================================
ScyllaDB Alternator Table Restore Tool
============================================================

Scanning for available backups...

Available table backups (3 total):
  1. users
  2. orders
  3. products

⚠️  WARNING: Restore will DROP existing tables and their data!

Options:
1. Restore a specific table
2. Restore all tables
3. Exit

Enter your choice (1, 2, or 3):
```

### Restoration Options

#### Option 1: Restore a Specific Table

Restores a single table with confirmation.

**Example:**
```
Enter your choice (1, 2, or 3): 1
Enter table name: users

⚠️  WARNING: This will DROP the existing 'users' table and all its data!
Are you sure you want to proceed? (yes/no): yes

2024-12-11 14:30:00 - INFO - ===== Start restore process for users =====
2024-12-11 14:30:00 - INFO - Dropping keyspace: alternator_users
2024-12-11 14:30:02 - INFO - Keyspace alternator_users dropped successfully
2024-12-11 14:30:02 - INFO - Keyspace data directory deleted
2024-12-11 14:30:02 - INFO - Ensuring keyspace exists: alternator_users
2024-12-11 14:30:03 - INFO - Keyspace alternator_users ensured to exist
2024-12-11 14:30:03 - INFO - Using separated schema files (table_schema.cql + materialized_view_*.cql)
2024-12-11 14:30:03 - INFO - Restoring base table schema for users
2024-12-11 14:30:04 - INFO - Base table schema restored successfully for users
2024-12-11 14:30:04 - INFO - Truncating table alternator_users.users
2024-12-11 14:30:05 - INFO - Table truncated successfully
2024-12-11 14:30:05 - INFO - Table ID for users: 330f8fd0aca211f0af61efb5703633f5
2024-12-11 14:30:05 - INFO - Using Table ID: 330f8fd0aca211f0af61efb5703633f5
2024-12-11 14:30:05 - INFO - Restoring data for users
2024-12-11 14:30:05 - INFO - Stopping ScyllaDB service...
2024-12-11 14:30:10 - INFO - ScyllaDB service stopped successfully
2024-12-11 14:30:10 - INFO - Data extracted to /var/lib/scylla/data/alternator_users/users-330f8fd0aca211f0af61efb5703633f5/
2024-12-11 14:30:10 - INFO - Starting ScyllaDB service...
2024-12-11 14:30:20 - INFO - ScyllaDB service started successfully
2024-12-11 14:30:20 - INFO - Running nodetool refresh for alternator_users.users
2024-12-11 14:30:22 - INFO - Nodetool refresh completed successfully
2024-12-11 14:30:22 - INFO - Restoring materialized views after data is loaded...
2024-12-11 14:30:22 - INFO - Looking for materialized views to restore for users
2024-12-11 14:30:22 - INFO - Found 2 materialized view(s) to restore
2024-12-11 14:30:22 - INFO - Restoring materialized view from materialized_view_1.cql
2024-12-11 14:30:23 - INFO - Materialized view restored successfully
2024-12-11 14:30:23 - INFO - Restoring materialized view from materialized_view_2.cql
2024-12-11 14:30:24 - INFO - Materialized view restored successfully
2024-12-11 14:30:24 - INFO - All materialized views processed for users
2024-12-11 14:30:24 - INFO - ===== Restore completed for users =====

✅ Table 'users' restored successfully!
```

#### Option 2: Restore All Tables

Restores all available backups with confirmation.

**Example:**
```
Enter your choice (1, 2, or 3): 2

⚠️  Are you sure you want to restore ALL 3 tables? This will DROP all existing tables! (yes/no): yes

Restoring 3 tables...

2024-12-11 14:35:00 - INFO - ===== Start restore process for users =====
...
2024-12-11 14:35:30 - INFO - ===== Restore completed for users =====

2024-12-11 14:35:30 - INFO - ===== Start restore process for orders =====
...
2024-12-11 14:36:00 - INFO - ===== Restore completed for orders =====

2024-12-11 14:36:00 - INFO - ===== Start restore process for products =====
...
2024-12-11 14:36:30 - INFO - ===== Restore completed for products =====

============================================================
Restore Summary:
  ✅ Successful: 3
  ❌ Failed: 0
  📊 Total: 3
============================================================

All tables restored successfully!
```

**If some tables fail:**
```
============================================================
Restore Summary:
  ✅ Successful: 2
  ❌ Failed: 1
  📊 Total: 3

Failed tables:
  - orders
============================================================
```

#### Option 3: Exit

Exits the script gracefully without making changes.

### Restoration Workflow Explained

The script follows a carefully ordered 8-step process:

#### Step 1: Determine Schema File Type

```python
if os.path.exists(f"{BACKUP_FOLDER}/table_schema.cql"):
    use_separated_schema = True  # New format (preferred)
elif os.path.exists(f"{BACKUP_FOLDER}/schema.cql"):
    use_separated_schema = False  # Legacy format
```

**Backward Compatibility:**
- ✅ Supports new separated schema format (`table_schema.cql` + `materialized_view_*.cql`)
- ✅ Supports legacy combined format (`schema.cql`)
- ✅ Automatically detects and logs which format is being used

#### Step 2: Drop Existing Keyspace

```bash
# Drop keyspace using CQL
cqlsh -e "DROP KEYSPACE IF EXISTS alternator_users;"

# Delete physical data directory
rm -rf /var/lib/scylla/data/alternator_users/
```

**Why needed:**
- ⚠️ **Destructive operation** - removes all existing data
- Ensures clean slate for restoration
- Removes both logical (CQL) and physical (filesystem) data
- Prevents conflicts with existing table structures

#### Step 3: Recreate Keyspace

```bash
cqlsh -e "CREATE KEYSPACE IF NOT EXISTS alternator_users 
          WITH REPLICATION = {
              'class': 'SimpleStrategy', 
              'replication_factor': 1
          };"
```

**Purpose:**
- Creates empty keyspace with proper replication settings
- Required before creating tables
- Sets replication strategy (SimpleStrategy for single-node)

#### Step 4: Restore Base Table Schema

```bash
# Apply base table DDL (without materialized views)
cqlsh -f ./backups/users/table_schema.cql
```

**What it restores:**
```sql
CREATE TABLE alternator_users.users (
    pk text,
    sk text,
    age int,
    name text,
    email text,
    PRIMARY KEY (pk, sk)
) WITH ...;
```

**Important:**
- ✅ Restores only the base table structure
- ✅ Does NOT restore materialized views yet
- ✅ Ensures base table exists before data restoration

#### Step 5: Truncate Table

```bash
cqlsh -e "TRUNCATE alternator_users.users;"
```

**Purpose:**
- Ensures table is completely empty
- Removes any data that might have been created during schema restoration
- Prepares clean state for SSTable restoration

#### Step 6: Get New Table ID

```bash
# Query for the new table UUID
SELECT id FROM system_schema.tables 
WHERE keyspace_name = 'alternator_users' 
  AND table_name = 'users';

# Returns: "330f8fd0aca211f0af61efb5703633f5" (without dashes)
```

**Why needed:**
- ScyllaDB stores table data in UUID-named directories
- Example: `/var/lib/scylla/data/alternator_users/users-330f8fd0aca211f0af61efb5703633f5/`
- UUID changes each time table is created
- Must get the **new UUID** (not the one from backup)

**Critical Detail:**
```
Backup UUID:   220f8fd0aca211f0af61efb5703633f5  (old)
Restored UUID: 330f8fd0aca211f0af61efb5703633f5  (new - different!)
```

#### Step 7: Restore Table Data

This is the most critical step - handles physical SSTable restoration.

**Sub-steps:**

**7a. Stop ScyllaDB Service**
```bash
systemctl stop scylla-server
sleep 5  # Wait for complete shutdown
```

**Why:**
- Cannot copy SSTable files while ScyllaDB is running
- SSTable files are memory-mapped and locked by ScyllaDB
- Copying while running could corrupt data

**7b. Extract Backup to Table Directory**
```bash
tar xzf ./backups/users/users_backup.tar.gz \
    -C /var/lib/scylla/data/alternator_users/users-330f8fd0aca211f0af61efb5703633f5/
```

**What's restored:**
- `mc-1-big-Data.db` - Actual table data
- `mc-1-big-Index.db` - Partition index
- `mc-1-big-Summary.db` - Index summary for faster lookups
- `mc-1-big-Statistics.db` - SSTable statistics
- `mc-1-big-TOC.txt` - Table of contents (lists all components)

**7c. Start ScyllaDB Service**
```bash
systemctl start scylla-server
sleep 10  # Wait for full startup
```

**Purpose:**
- Starts ScyllaDB to recognize new files
- Waits for complete startup before proceeding

**7d. Refresh Table**
```bash
nodetool refresh alternator_users users
```

**Critical Command:**
- ✅ Tells ScyllaDB to load the new SSTable files
- ✅ Rebuilds internal metadata and indexes
- ✅ Without refresh, ScyllaDB won't see the restored data
- ✅ Makes data available for queries

**Complete Flow:**
```
Running ScyllaDB
    ↓
Stop Service (systemctl stop)
    ↓
Copy SSTable Files (tar xzf)
    ↓
Start Service (systemctl start)
    ↓
Refresh Table (nodetool refresh)
    ↓
Data Available for Queries
```

#### Step 8: Restore Materialized Views

**Only if using separated schema format:**

```bash
# Apply each materialized view in sequence
cqlsh -f ./backups/users/materialized_view_1.cql
cqlsh -f ./backups/users/materialized_view_2.cql
```

**Example materialized view:**
```sql
CREATE MATERIALIZED VIEW alternator_users.users_by_age AS
    SELECT pk, sk, age, name
    FROM alternator_users.users
    WHERE age IS NOT NULL AND pk IS NOT NULL AND sk IS NOT NULL
    PRIMARY KEY (age, pk, sk)
    WITH ...;
```

**Why AFTER data restoration:**
- ✅ Base table must exist first
- ✅ Base table must have data
- ✅ Views automatically populate from base table data
- ✅ ScyllaDB handles view population efficiently

**Error Handling:**
- If a view fails, script logs warning and continues
- Other views still get restored
- Base table restoration is prioritized

**Legacy Format:**
```
If using schema.cql:
- Materialized views included in single file
- Applied together with base table schema
- Still works, but separated format is preferred
```

---

### Why Restoration Order Matters

#### ✅ Correct Order (Script's Approach)

```
1. DROP KEYSPACE                    ← Remove old data/structure
2. CREATE KEYSPACE                  ← Recreate keyspace
3. CREATE TABLE (base only)         ← Create empty base table
4. TRUNCATE TABLE                   ← Ensure completely empty
5. Get Table ID                     ← Get new UUID for directory path
6. Stop ScyllaDB                    ← Prepare for file operations
7. Copy SSTable files               ← Restore data files
8. Start ScyllaDB                   ← Load ScyllaDB with new files
9. nodetool refresh                 ← Tell ScyllaDB about new files
10. CREATE MATERIALIZED VIEW        ← Views auto-populate from data
```

#### ❌ Why Wrong Order Fails

**Problem 1: Creating views before base table**
```
❌ CREATE MATERIALIZED VIEW first
   → View references non-existent base table
   → ERROR: Base table 'users' does not exist

✅ CREATE TABLE first, then views
   → Views can reference existing base table
   → SUCCESS
```

**Problem 2: Restoring data before schema**
```
❌ Copy SSTable files before CREATE TABLE
   → ScyllaDB doesn't know table structure
   → Files ignored or cause schema mismatch errors

✅ CREATE TABLE first, then copy files
   → ScyllaDB knows how to interpret files
   → Data loaded correctly
```

**Problem 3: Starting ScyllaDB before copying files**
```
❌ ScyllaDB running while copying files
   → File locks prevent copying
   → Potential data corruption
   → Partial writes

✅ Stop ScyllaDB, copy files, then start
   → No locks or conflicts
   → Clean, atomic operation
```

**Problem 4: Creating views without data**
```
❌ CREATE MATERIALIZED VIEW before data restore
   → View is empty
   → When data restored, view doesn't populate automatically
   → Requires manual rebuild

✅ Restore data first, then CREATE MATERIALIZED VIEW
   → ScyllaDB automatically populates view from existing data
   → Efficient bulk population
```

---

### Restoration Function Reference

#### `start_scylla_service()`

**Purpose:** Start ScyllaDB service after file operations.

**Returns:** 
- `True`: Service started successfully
- `False`: Failed to start service

**Wait Time:** 10 seconds for full startup

**Example:**
```python
if not start_scylla_service():
    logger.error("Failed to start ScyllaDB")
    return False
```

---

#### `stop_scylla_service()`

**Purpose:** Stop ScyllaDB service before file operations.

**Returns:** 
- `True`: Service stopped successfully
- `False`: Failed to stop service

**Wait Time:** 5 seconds for complete shutdown

**Critical:** Must be stopped before copying SSTable files

---

#### `drop_keyspace(keyspace)`

**Purpose:** Complete removal of keyspace (logical + physical).

**Parameters:**
- `keyspace` (str): Keyspace name (e.g., "alternator_users")

**Returns:** 
- `True`: Keyspace dropped successfully
- `False`: Error occurred

**Operations:**
1. Drops keyspace using CQL: `DROP KEYSPACE IF EXISTS`
2. Deletes physical directory: `rm -rf /var/lib/scylla/data/{keyspace}/`

**Warning:** ⚠️ Destructive operation - all data lost!

---

#### `ensure_keyspace_exists(keyspace)`

**Purpose:** Create keyspace with proper replication settings.

**Parameters:**
- `keyspace` (str): Keyspace name

**Returns:** 
- `True`: Keyspace created/exists
- `False`: Error occurred

**Replication Settings:**
```python
CREATE KEYSPACE IF NOT EXISTS alternator_users 
WITH REPLICATION = {
    'class': 'SimpleStrategy', 
    'replication_factor': 1
};
```

---

#### `get_table_id(table_name)`

**Purpose:** Get the internal UUID for a table after restoration.

**Parameters:**
- `table_name` (str): Name of the table

**Returns:** 
- `str`: Table UUID without dashes (e.g., "330f8fd0aca211f0af61efb5703633f5")
- `None`: Table not found or error

**Important:** Gets the **new** UUID after table recreation (different from backup UUID)

**Example:**
```python
table_id = get_table_id("users")
# Returns: "330f8fd0aca211f0af61efb5703633f5"

# Used to construct path:
# /var/lib/scylla/data/alternator_users/users-330f8fd0aca211f0af61efb5703633f5/
```

---

#### `restore_table_schema(table_name, schema_file)`

**Purpose:** Restore base table schema (without materialized views).

**Parameters:**
- `table_name` (str): Name of the table
- `schema_file` (str): Path to schema file

**Returns:** 
- `True`: Schema restored successfully
- `None`: Error occurred

**Schema File Options:**
- Preferred: `./backups/{table_name}/table_schema.cql` (base table only)
- Legacy: `./backups/{table_name}/schema.cql` (combined format)

**What's Restored:**
- Table structure (columns, data types)
- Primary key and clustering key
- Table properties (compression, compaction, etc.)
- **Does NOT restore** materialized views (handled separately)

---

#### `restore_materialized_views(table_name, backup_folder)`

**Purpose:** Restore materialized views from separated CQL files.

**Parameters:**
- `table_name` (str): Name of the table
- `backup_folder` (str): Path to backup directory

**Returns:** 
- `True`: All views processed (some may have failed with warnings)

**Behavior:**
- Finds all `materialized_view_*.cql` files
- Applies views in sorted order (materialized_view_1.cql, materialized_view_2.cql, etc.)
- If a view fails, logs warning and continues with remaining views
- Views automatically populate from base table data

**Error Handling Strategy:**
```python
try:
    apply_view(view_file)
    logger.info(f"✓ View restored: {view_name}")
except:
    logger.warning(f"⚠ View failed: {view_name}, continuing...")
    # Don't return False - continue with other views
```

**Why Resilient:**
- Base table restoration is most critical
- Some views might have complex dependencies
- Better to restore partial views than fail completely

---

#### `truncate_table(keyspace, table_name)`

**Purpose:** Empty table before data restoration.

**Parameters:**
- `keyspace` (str): Keyspace name
- `table_name` (str): Table name

**Returns:** 
- `True`: Table truncated successfully
- `False`: Error occurred

**Why Needed:**
- Schema restoration might create initial data
- Ensures completely clean state for SSTable restoration
- Prevents data conflicts

---

#### `restore_table_data(table_name, backup_file, table_id)`

**Purpose:** Complete physical data restoration process.

**Parameters:**
- `table_name` (str): Name of the table
- `backup_file` (str): Path to backup archive (.tar.gz)
- `table_id` (str): Table UUID (without dashes)

**Returns:** 
- `True`: Data restored successfully
- `False`: Error occurred

**Process Flow:**
1. Verify backup file exists
2. Stop ScyllaDB service
3. Extract backup to table data directory
4. Start ScyllaDB service
5. Run `nodetool refresh` to load new SSTables

**Critical Steps:**
```python
# Must stop service
systemctl stop scylla-server

# Extract files
tar xzf backup.tar.gz -C /var/lib/scylla/data/...

# Must start service
systemctl start scylla-server

# Must refresh to load files
nodetool refresh keyspace table
```

**Error Recovery:**
- If extraction fails → Restarts ScyllaDB before returning
- If refresh fails → Logs error but service remains running

---

#### `get_all_backup_tables()`

**Purpose:** Scan for all available table backups.

**Parameters:** None

**Returns:** 
- `list`: List of table names with valid backups
- `[]`: Empty list if no backups found

**Validation:**
Each backup must have:
- Schema file: `table_schema.cql` OR `schema.cql`
- Backup archive: `{table_name}_backup.tar.gz`

**Example:**
```python
tables = get_all_backup_tables()
# Returns: ['users', 'orders', 'products']
```

**Used By:**
- Interactive menu to display available backups
- Batch restore to determine which tables to process

---

#### `restore_table(table_name)`

**Purpose:** Complete orchestration of table restoration.

**Parameters:**
- `table_name` (str): Name of the table to restore

**Returns:** 
- `True`: Restoration completed successfully
- `False`: Restoration failed at any step

**Complete Workflow:**
```python
1. Determine schema format (separated vs legacy)
2. Drop existing keyspace
3. Recreate keyspace
4. Restore base table schema
5. Truncate table
6. Get new table ID
7. Restore table data (Stop → Copy → Start → Refresh)
8. Restore materialized views (if separated schema)
```

**Error Handling:**
- Fail-fast strategy: If any critical step fails, returns False immediately
- Materialized view errors: Logs warnings but continues
- Logs all operations to both console and file

**Backward Compatibility:**
```python
# Prefers new separated format
if exists("table_schema.cql"):
    use_separated_schema = True
    restore_schema("table_schema.cql")
    # ... restore data ...
    restore_materialized_views()

# Falls back to legacy format
elif exists("schema.cql"):
    use_separated_schema = False
    restore_schema("schema.cql")  # Includes views
    # ... restore data ...
```

---

### Restoration Logging

#### Dual Output

Logs are written to both console and file for complete visibility:

```python
logging.basicConfig(
    handlers=[
        logging.FileHandler('alternator_restore.log'),  # Persistent audit trail
        logging.StreamHandler()                          # Real-time console output
    ]
)
```

**Benefits:**
- **Console:** Real-time feedback for operator monitoring
- **Log File:** Detailed audit trail for troubleshooting and compliance

#### Log File Location

- **Path:** `./alternator_restore.log`
- **Format:** `2024-12-11 14:30:00 - INFO - Message`
- **Retention:** Append mode (keeps all historical logs)

#### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| **INFO** | Normal operations | `✓ Table schema restored successfully` |
| **WARNING** | Non-critical issues | `⚠ Materialized view failed, continuing...` |
| **ERROR** | Critical failures | `✗ Failed to restore schema` |
| **EXCEPTION** | Unexpected errors | `Unexpected error with full traceback` |

#### Example Log Output

```
2024-12-11 14:30:00 - INFO - ===== Start restore process for users =====
2024-12-11 14:30:00 - INFO - Dropping keyspace: alternator_users
2024-12-11 14:30:02 - INFO - Keyspace alternator_users dropped successfully
2024-12-11 14:30:02 - INFO - Using separated schema files (table_schema.cql + materialized_view_*.cql)
2024-12-11 14:30:03 - INFO - Restoring base table schema for users
2024-12-11 14:30:04 - INFO - Base table schema restored successfully
2024-12-11 14:30:05 - INFO - Table ID for users: 330f8fd0aca211f0af61efb5703633f5
2024-12-11 14:30:05 - INFO - Stopping ScyllaDB service...
2024-12-11 14:30:10 - INFO - ScyllaDB service stopped successfully
2024-12-11 14:30:10 - INFO - Data extracted to /var/lib/scylla/data/...
2024-12-11 14:30:10 - INFO - Starting ScyllaDB service...
2024-12-11 14:30:20 - INFO - ScyllaDB service started successfully
2024-12-11 14:30:22 - INFO - Found 2 materialized view(s) to restore
2024-12-11 14:30:23 - INFO - Materialized view restored successfully
2024-12-11 14:30:24 - INFO - All materialized views processed
2024-12-11 14:30:24 - INFO - ===== Restore completed for users =====
```

---

### Error Handling Strategies

#### Fail-Fast for Critical Steps

For single table restoration, the script stops immediately on critical failures:

```python
if not drop_keyspace(KEYSPACE):
    logger.error("Failed to drop keyspace")
    return False  # Stop immediately

if not restore_table_schema(table_name, SCHEMA_FILE):
    logger.error("Failed to restore schema")
    return False  # Stop immediately

if not restore_table_data(table_name, BACKUP_FILE, TABLE_ID):
    logger.error("Failed to restore data")
    return False  # Stop immediately
```

**Rationale:**
- If schema fails, data restoration is meaningless
- If data fails, materialized views will be empty
- Prevents partially restored state that could cause confusion

#### Continue-on-Error for Views

Materialized view restoration is more resilient:

```python
for view_file in view_files:
    try:
        restore_view(view_file)
        logger.info(f"✓ View restored: {view_file}")
    except Exception as e:
        logger.warning(f"⚠ View failed: {view_file}, error: {e}")
        # Don't return False - continue with remaining views
```

**Rationale:**
- Base table restoration is most important
- Some views might fail due to complex dependencies
- Better to have base table + partial views than nothing
- Operator can manually recreate failed views later

#### Batch Restore Resilience

For batch restoration (Option 2), the script continues even if individual tables fail:

```python
success_count = 0
failed_tables = []

for table_name in tables:
    logger.info(f"Processing table: {table_name}")
    if restore_table(table_name):
        success_count += 1
        logger.info(f"✅ {table_name} restored successfully")
    else:
        failed_tables.append(table_name)
        logger.error(f"❌ {table_name} failed to restore")
        # Continue with next table instead of stopping
```

**Benefits:**
- One failed table doesn't stop entire batch
- Summary shows which tables succeeded/failed
- Operator can retry failed tables individually
- Maximizes successful restorations

#### Service Recovery

If operations fail during data restoration, the script ensures ScyllaDB service is restarted:

```python
try:
    stop_scylla_service()
    extract_backup_files()
    start_scylla_service()
    run_nodetool_refresh()
except Exception as e:
    logger.error(f"Data restoration failed: {e}")
    start_scylla_service()  # Ensure service is running
    return False
```

**Safety:**
- ScyllaDB won't be left in stopped state
- System remains operational even if restore fails
- Prevents cascading failures

---

### Restoration Troubleshooting

#### Issue: Permission Denied

**Symptoms:**
```
ERROR - Failed to stop ScyllaDB service: Permission denied
ERROR - Failed to delete keyspace directory: Permission denied
```

**Solution:**
```bash
# Run with sudo
sudo python3 restore.py

# Or grant appropriate permissions
sudo usermod -aG scylla $USER
```

---

#### Issue: ScyllaDB Won't Stop

**Symptoms:**
```
ERROR - Failed to stop ScyllaDB service: Timeout
ERROR - Service still running after stop command
```

**Diagnosis:**
```bash
# Check ScyllaDB status
systemctl status scylla-server

# Check for stuck processes
ps aux | grep scylla
```

**Solution:**
```bash
# Force stop
sudo systemctl kill scylla-server
sudo systemctl stop scylla-server

# If still stuck, force kill
sudo killall -9 scylla
```

---

#### Issue: Nodetool Refresh Failed

**Symptoms:**
```
ERROR - Error running nodetool refresh: Connection refused
ERROR - Error running nodetool refresh: Timeout
```

**Diagnosis:**
```bash
# Check nodetool connectivity
nodetool status

# Check if ScyllaDB is fully started
journalctl -u scylla-server -n 50
```

**Solution:**
```bash
# Wait longer for ScyllaDB to fully start
sleep 20
nodetool refresh alternator_users users

# Check ScyllaDB logs for issues
tail -f /var/log/scylla/scylla.log
```

---

#### Issue: Table ID Not Found

**Symptoms:**
```
ERROR - Table ID not found for users
```

**Diagnosis:**
```bash
# Check if table was created
cqlsh -u cassandra -p cassandra -e "DESC TABLE alternator_users.users;"

# Check system schema
cqlsh -u cassandra -p cassandra -e "SELECT * FROM system_schema.tables WHERE keyspace_name = 'alternator_users';"
```

**Solution:**
1. Verify schema file is valid CQL
2. Check for syntax errors in schema file
3. Ensure keyspace exists before table creation
4. Review cqlsh error messages

---

#### Issue: Backup Files Not Found

**Symptoms:**
```
ERROR - Backup folder ./backups/users does not exist
ERROR - Schema file ./backups/users/table_schema.cql does not exist
```

**Solution:**
```bash
# Check backup directory structure
ls -la ./backups/
ls -la ./backups/users/

# Verify required files exist
ls -la ./backups/users/table_schema.cql
ls -la ./backups/users/users_backup.tar.gz

# If using legacy format
ls -la ./backups/users/schema.cql
```

---

#### Issue: Materialized View Restoration Failed

**Symptoms:**
```
WARNING - Error restoring materialized view from materialized_view_1.cql
```

**Diagnosis:**
```bash
# Manually test view creation
cqlsh -u cassandra -p cassandra -f ./backups/users/materialized_view_1.cql

# Check for view dependencies
cat ./backups/users/materialized_view_1.cql
```

**Common Causes:**
1. View references columns not in base table
2. View primary key doesn't include all base table primary keys
3. Syntax errors in view definition
4. Base table not fully populated

**Solution:**
```bash
# Manually recreate view after fixing issues
# Edit materialized_view_1.cql
nano ./backups/users/materialized_view_1.cql

# Apply manually
cqlsh -u cassandra -p cassandra -f ./backups/users/materialized_view_1.cql

# Verify view is populating
cqlsh -u cassandra -p cassandra -e "SELECT COUNT(*) FROM alternator_users.view_name;"
```

---

#### Issue: Disk Space

**Symptoms:**
```
ERROR - Failed to extract backup file: No space left on device
```

**Diagnosis:**
```bash
# Check available disk space
df -h /var/lib/scylla/data/

# Check backup size
du -sh ./backups/users/users_backup.tar.gz

# Check extracted size (multiply by ~2 for decompression)
```

**Solution:**
```bash
# Free up space
sudo nodetool clearsnapshot
sudo rm -rf /var/lib/scylla/data/*/*/snapshots/*

# Or expand disk
# (platform-specific commands)
```

---

### Verification After Restoration

#### Verify Table Data

```bash
# Count rows
cqlsh -u cassandra -p cassandra -e "SELECT COUNT(*) FROM alternator_users.users;"

# Sample data
cqlsh -u cassandra -p cassandra -e "SELECT * FROM alternator_users.users LIMIT 10;"

# Check via Alternator
aws dynamodb scan \
    --table-name users \
    --endpoint-url http://localhost:8000 \
    --region us-east-1 \
    --max-items 10
```

#### Verify Materialized Views

```bash
# List all materialized views
cqlsh -u cassandra -p cassandra -e "SELECT * FROM system_schema.views WHERE keyspace_name = 'alternator_users';"

# Check view data
cqlsh -u cassandra -p cassandra -e "SELECT COUNT(*) FROM alternator_users.users_by_age;"

# Verify view is populating correctly
cqlsh -u cassandra -p cassandra -e "SELECT * FROM alternator_users.users_by_age LIMIT 10;"
```

#### Verify SSTable Files

```bash
# List SSTable files
ls -lh /var/lib/scylla/data/alternator_users/users-*/

# Check SSTable statistics
nodetool tablestats alternator_users.users

# Verify SSTable integrity
nodetool verify alternator_users users
```

#### Performance Verification

```bash
# Check read latency
nodetool cfstats alternator_users.users | grep -i latency

# Run compaction if needed
nodetool compact alternator_users users

# Check for any errors
journalctl -u scylla-server --since "10 minutes ago" | grep -i error
```

---

### Best Practices for Restoration

#### 1. Test Restoration in Non-Production First

```bash
# Always test restore process in dev/staging
# before running in production

# Use a test table first
sudo python3 restore.py
# Select option 1 and restore a small test table
```

#### 2. Verify Backups Before Restoration

```bash
# Check backup integrity
tar tzf ./backups/users/users_backup.tar.gz | head

# Validate schema files
cat ./backups/users/table_schema.cql | grep "CREATE TABLE"
cat ./backups/users/materialized_view_1.cql | grep "CREATE MATERIALIZED VIEW"

# Check backup size
du -sh ./backups/users/
```

#### 3. Monitor During Restoration

```bash
# In separate terminal, tail logs
tail -f alternator_restore.log

# Monitor ScyllaDB logs
tail -f /var/log/scylla/scylla.log

# Monitor system resources
htop
iostat -x 5
```

#### 4. Have Rollback Plan

```bash
# Before restore, take current snapshot
nodetool snapshot alternator_users -t before_restore

# If restore fails, you can roll back to this snapshot
# (requires separate restore script run)
```

#### 5. Schedule During Maintenance Window

```bash
# Restoration involves service restarts
# Schedule during planned downtime

# Estimate time needed:
# - Small table (< 100 MB): 2-5 minutes
# - Medium table (1 GB): 10-20 minutes
# - Large table (10 GB): 30-60 minutes
```

#### 6. Document Restoration

```bash
# Create restoration log
cat > restoration_notes.txt << EOF
Date: $(date)
Table: users
Backup Date: 2024-12-10
Operator: $USER
Reason: Data recovery after accidental deletion
Result: Success
Verification: SELECT COUNT(*) = 1000000 rows
EOF
```

---

### Security Considerations for Restoration

#### Root Access Required

```bash
# Restoration requires root/sudo for:
# - Stopping/starting systemctl services
# - Writing to /var/lib/scylla/data/
# - Deleting system directories

# Run with sudo
sudo python3 restore.py
```

#### Credential Management

**Current Configuration (Development Only):**
```python
AWS_ACCESS_KEY_ID = 'cassandra'
AWS_SECRET_ACCESS_KEY = '$6$Wss/K5OMZ4tbUfRh$...'
```

⚠️ **Warning:** Hardcoded credentials are suitable only for local development!

**Production Recommendations:**
```python
# Use environment variables
AWS_ACCESS_KEY_ID = os.getenv('SCYLLA_USER')
AWS_SECRET_ACCESS_KEY = os.getenv('SCYLLA_PASSWORD')

# Or use configuration file
import configparser
config = configparser.ConfigParser()
config.read('/etc/scylla/credentials.conf')
```

#### Backup File Security

```bash
# Restrict access to backup files
chmod 600 ./backups/*/*.tar.gz
chmod 600 ./backups/*/*.cql

# Encrypt backups at rest
gpg --encrypt --recipient admin@example.com users_backup.tar.gz

# Use encrypted filesystems
# LUKS, eCryptfs, or cloud encryption
```

#### Audit Trail

```bash
# Restoration logs provide audit trail
# alternator_restore.log contains:
# - What was restored
# - When it was restored
# - Who restored it (via system user)
# - Whether it succeeded/failed

# Archive logs for compliance
tar czf restore_logs_$(date +%Y%m%d).tar.gz alternator_restore.log
```

---

### Important Notes for Restoration

#### ScyllaDB Best Practices

The restoration script follows ScyllaDB's recommended approach:

```
✅ DO: Restore base table, then recreate materialized views
✅ DO: Use nodetool refresh after copying SSTables
✅ DO: Stop ScyllaDB before copying files
✅ DO: Verify data integrity after restoration

❌ DON'T: Restore materialized view SSTables directly
❌ DON'T: Copy files while ScyllaDB is running
❌ DON'T: Skip nodetool refresh step
❌ DON'T: Restore to a different ScyllaDB version without testing
```

#### UUID Changes

```python
# Important: Table UUIDs change on every CREATE TABLE
# Backup UUID:   220f8fd0aca211f0af61efb5703633f5
# Restored UUID: 330f8fd0aca211f0af61efb5703633f5  (different!)

# Script automatically:
# 1. Gets new UUID after table creation
# 2. Uses new UUID for directory path
# 3. Copies SSTables to correct location
```

#### Materialized View Population

```sql
-- Views automatically populate from base table data
-- No manual intervention needed

CREATE MATERIALIZED VIEW users_by_age AS ...;
-- ScyllaDB reads base table
-- Populates view in background
-- Process is automatic and efficient
```

#### Service Restarts

```bash
# Restoration involves ScyllaDB restarts
# Expect brief downtime:
# - Stop service: ~5 seconds
# - Copy files: ~variable (based on data size)
# - Start service: ~10 seconds
# - Refresh table: ~variable (based on data size)

# Total downtime: Typically 30-60 seconds + copy time
```

---

## Related Documentation

- [ScyllaDB Alternator Documentation](https://docs.scylladb.com/stable/using-scylla/alternator/)
- [ScyllaDB Backup and Restore](https://docs.scylladb.com/stable/operating-scylla/procedures/backup-restore/)
- [ScyllaDB Materialized Views](https://docs.scylladb.com/stable/cql/mv/)
- [ScyllaDB Nodetool Reference](https://docs.scylladb.com/stable/operating-scylla/nodetool/)
- [ScyllaDB SSTable Format](https://docs.scylladb.com/stable/architecture/sstable/)
- [Boto3 DynamoDB Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)

---

## Version History

- **v1.2** - Current release
  - ✅ Added comprehensive restoration documentation
  - ✅ Documented restoration workflow step-by-step
  - ✅ Added troubleshooting guide for common issues
  - ✅ Documented error handling strategies
  - ✅ Added verification procedures
  - ✅ Included best practices and security considerations

- **v1.1** - Backup improvements
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

---

**Note:** This tool is designed for production use with proper error handling, logging, and materialized view separation. Always test in a non-production environment first and verify backups can be restored successfully, paying special attention to the restoration order of base tables and their materialized views.
