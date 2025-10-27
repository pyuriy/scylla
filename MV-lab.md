# Comprehensive ScyllaDB Materialized Views Lab for ScyllaDB v4.6

## Overview
This hands-on lab guides you through the creation, usage, and maintenance of Materialized Views (MVs) in ScyllaDB version 4.6. MVs are automatically maintained, read-only tables that denormalize data from a base table to support efficient queries on non-primary key columns. This lab uses a simple user management scenario to demonstrate key concepts.

**Duration**: 30-45 minutes  
**Objectives**:  
- Set up a ScyllaDB 4.6 single-node cluster using Docker.  
- Create a base table and insert data.  
- Build multiple MVs for different query patterns.  
- Query MVs and observe automatic synchronization.  
- Explore updates, deletes, and performance implications.  
- Understand limitations and best practices.  

**Prerequisites**:  
- Docker installed (version 20+ recommended).  
- Basic familiarity with CQL and command-line tools.  
- Access to a terminal.  

**Note**: This lab uses ScyllaDB Open Source 4.6, which has no specific changes to MVs compared to prior stable versions—features remain consistent and production-ready. For multi-node setups or enterprise features, refer to official docs.

## Lab Setup: Running ScyllaDB 4.6 in Docker
We'll run a single-node ScyllaDB cluster for simplicity. This setup includes cqlsh for querying.

### Step 1: Pull and Run the ScyllaDB Container
1. Open a terminal and pull the ScyllaDB 4.6 image:  
   ```bash
   docker pull scylladb/scylla:4.6
   ```

2. Run the container with port mappings for CQL (9042) and nodetool (7199):  
   ```bash
   docker run --name scylla-node -d --hostname scylla-node -p 9042:9042 -p 7199:7199 scylladb/scylla:4.6 --overprovisioned --smp 2 --memory=2G --developer-mode 1
   ```
   - `--overprovisioned`: Enables higher I/O for lab performance.  
   - `--developer-mode 1`: Disables strict checks for easier experimentation.  
   - Adjust `--smp` and `--memory` based on your machine.

3. Verify the container is running:  
   ```bash
   docker ps
   ```
   You should see `scylla-node` with status "Up".

### Step 2: Connect to ScyllaDB Using cqlsh
1. Exec into the container and start cqlsh:  
   ```bash
   docker exec -it scylla-node cqlsh
   ```
   - You'll enter the CQL shell: `cqlsh>`. All subsequent CQL commands run here.  
   - To exit cqlsh later: `exit;`.

2. Check ScyllaDB version:  
   ```cql
   SELECT version FROM system.local;
   ```
   - Expected: Output showing "4.6.x" or similar.

### Step 3: Create a Keyspace
1. Create a keyspace with simple replication (for single-node):  
   ```cql
   CREATE KEYSPACE IF NOT EXISTS lab_mv WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
   USE lab_mv;
   ```
   - `SimpleStrategy` is fine for single-node; use `NetworkTopologyStrategy` for clusters.

## Part 1: Creating and Populating the Base Table
We'll use a `users` base table with `user_id` as the primary key, but queries often target `email`, `age`, or `name`.

### Step 1.1: Define the Base Table
```cql
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INT
);
```

### Step 1.2: Insert Sample Data
Insert 5 users (use `uuid()` for unique IDs):  
```cql
INSERT INTO users (user_id, name, email, age) VALUES (uuid(), 'Alice Johnson', 'alice@example.com', 30);
INSERT INTO users (user_id, name, email, age) VALUES (uuid(), 'Bob Smith', 'bob@example.com', 25);
INSERT INTO users (user_id, name, email, age) VALUES (uuid(), 'Charlie Brown', 'charlie@example.com', 35);
INSERT INTO users (user_id, name, email, age) VALUES (uuid(), 'Diana Prince', 'diana@example.com', 28);
INSERT INTO users (user_id, name, email, age) VALUES (uuid(), 'Eve Davis', 'eve@example.com', 32);
```

### Step 1.3: Verify the Base Table
```cql
SELECT * FROM users;
```
- Expected: 5 rows displayed.  
- Describe the schema:  
  ```cql
  DESCRIBE TABLE users;
  ```

## Part 2: Creating Materialized Views
MVs must include all base primary key columns (`user_id`) in their SELECT and PRIMARY KEY, with `IS NOT NULL` in WHERE.

### Step 2.1: MV for Email Lookups (`user_by_email`)
This MV partitions by `email` for fast unique lookups.  
```cql
CREATE MATERIALIZED VIEW IF NOT EXISTS user_by_email AS
SELECT user_id, name, email, age
FROM users
WHERE user_id IS NOT NULL AND email IS NOT NULL
PRIMARY KEY ((email), user_id);
```

### Step 2.2: MV for Age-Based Queries (`user_by_age`)
This groups users by `age` (partition key) for range queries.  
```cql
CREATE MATERIALIZED VIEW IF NOT EXISTS user_by_age AS
SELECT user_id, name, email, age
FROM users
WHERE user_id IS NOT NULL AND age IS NOT NULL
PRIMARY KEY ((age), user_id);
```

### Step 2.3: MV for Name Prefix Searches (`user_by_name`)
This uses `name` as partition key, assuming prefix-based clustering.  
```cql
CREATE MATERIALIZED VIEW IF NOT EXISTS user_by_name AS
SELECT user_id, name, email, age
FROM users
WHERE user_id IS NOT NULL AND name IS NOT NULL
PRIMARY KEY ((name), user_id);
```

### Step 2.4: Verify MVs
```cql
DESCRIBE TABLES;
```
- Expected: Lists `users`, `user_by_email`, `user_by_age`, `user_by_name`.  
- Inspect one:  
  ```cql
  DESCRIBE TABLE user_by_email;
  ```

## Part 3: Querying Materialized Views
Query MVs like tables—no joins needed. Changes to the base propagate automatically (eventual consistency).

### Step 3.1: Query by Email (Efficient with MV)
```cql
SELECT * FROM user_by_email WHERE email = 'alice@example.com';
```
- Expected: Alice's row.  

**Contrast with Base Table (Inefficient)**:  
```cql
SELECT * FROM users WHERE email = 'alice@example.com' ALLOW FILTERING;
```
- Works but scans all partitions—avoid in production.

### Step 3.2: Query by Age Range
```cql
SELECT * FROM user_by_age WHERE age = 30 ALLOW FILTERING;
```
- Expected: Alice's row. (ALLOW FILTERING needed if no clustering on other cols.)  

### Step 3.3: Query by Name
```cql
SELECT * FROM user_by_name WHERE name = 'Bob Smith';
```
- Expected: Bob's row.

### Step 3.4: Full Scan on MV
```cql
SELECT * FROM user_by_age;
```
- Expected: All 5 rows, sorted by age.

## Part 4: Observing Synchronization
Updates to the base table sync to all MVs synchronously in v4.6 (with coordinator ensuring consistency).

### Step 4.1: Update a Record
Update Bob's age to 26:  
```cql
-- First, find Bob's user_id (run SELECT * FROM users; and note it)
UPDATE users SET age = 26 WHERE user_id = <bob_user_id>;
```

### Step 4.2: Verify Propagation
```cql
-- Check base
SELECT * FROM users WHERE user_id = <bob_user_id>;

-- Check MVs
SELECT * FROM user_by_age WHERE age = 26;
SELECT * FROM user_by_email WHERE email = 'bob@example.com';
```
- Expected: All show age=26.

### Step 4.3: Delete a Record
Delete Eve:  
```cql
DELETE FROM users WHERE user_id = <eve_user_id>;
```

### Step 4.4: Verify Deletion
```cql
SELECT COUNT(*) FROM users;  -- Should be 4
SELECT COUNT(*) FROM user_by_email;  -- Should be 4
```
- Deletions propagate automatically.

## Part 5: Performance and Monitoring
### Step 5.1: Basic Metrics with Nodetool
Exit cqlsh (`exit;`), then in the host terminal:  
```bash
docker exec -it scylla-node nodetool cfstats lab_mv.users
```
- Look for `Compacted row size`, `Read count`—MVs will show similar stats.

Re-enter cqlsh:  
```bash
docker exec -it scylla-node cqlsh
```

### Step 5.2: Simulate Load (Optional)
Insert 100 users in a loop (use a script or repeat inserts). Query MVs before/after to see latency differences.

## Part 6: Advanced Exercises
1. **Create a Composite MV**: Add a `city` column to `users`, insert data, and create an MV with PRIMARY KEY ((age, city), user_id). Query by age and city.  
2. **Secondary Index via MV**: Instead of manual MV, create `CREATE INDEX ON users (email);`—observe the auto-generated MV.  
3. **Error Handling**: Try creating an MV without `user_id` in SELECT—note the error. Fix it.  
4. **Drop MV**: `DROP MATERIALIZED VIEW user_by_name;` then recreate and re-insert data to observe rebuild.

## Limitations and Best Practices
| Aspect | Details |
|--------|---------|
| **Storage Overhead** | MVs duplicate data; monitor with `nodetool cfstats`. Limit columns in SELECT. |
| **Write Amplification** | Each update hits base + all MVs (e.g., 4x for 3 MVs). Use for read-heavy workloads. |
| **Consistency** | Eventual; use higher CL (e.g., QUORUM) for reads if needed. |
| **Restrictions** | No MVs on counters/collections; must include all base PK cols; no nesting. |
| **Best Practices** | One MV per query pattern; test write latency; drop unused MVs to save space. |

- **When to Use**: For non-PK filters without full scans. Alternatives: App-level denorm or Buckets pattern.

## Cleanup
1. Drop keyspace (drops all tables/MVs):  
   ```cql
   DROP KEYSPACE lab_mv;
   ```
2. Stop container:  
   ```bash
   docker stop scylla-node && docker rm scylla-node
   ```

## Additional Resources
- [Official ScyllaDB 4.6 Docs: Materialized Views](https://docs.scylladb.com/manual/4.6/features/materialized-views.html)  
- [ScyllaDB University: MV Hands-On Lab](https://university.scylladb.com/courses/data-modeling/lessons/materialized-views-secondary-indexes-and-filtering/topic/materialized-views-hands-on-lab/)  
- [Docker Best Practices](https://docs.scylladb.com/manual/stable/operating-scylla/procedures/tips/best-practices-scylla-on-docker.html)  
- Release Notes: [ScyllaDB 4.6](https://www.scylladb.com/product/release-notes/scylla-open-source-4-6/)

Experiment freely—ScyllaDB's developer mode forgives errors! If issues arise, check logs: `docker logs scylla-node`. Share feedback for improvements.
