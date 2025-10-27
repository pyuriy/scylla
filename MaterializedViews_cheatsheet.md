# ScyllaDB Materialized Views Cheatsheet

## Overview
Materialized Views (MVs) in ScyllaDB are read-only, automatically maintained secondary indexes that store a denormalized subset of data from a base table. They enable efficient querying on non-primary key columns by acting as global indexes, distributed across cluster nodes. Unlike traditional views, MVs are precomputed tables that stay synchronized with the base table via automatic propagation of inserts, updates, and deletes. In ScyllaDB, both Global and Local Secondary Indexes (GSI/LSI) are implemented using MVs under the hood, providing server-side denormalization without application-level complexity.

## Key Concepts
| Concept | Description |
|---------|-------------|
| **Base Table** | Original table; all DML operations (INSERT/UPDATE/DELETE) propagate to the MV. |
| **Query Definition** | SELECT statement defining the MV's structure, including required primary key columns. |
| **Automatic Synchronization** | No manual refreshes needed; changes to base table instantly update the MV. |
| **Read-Only** | Queries only; no direct writes to MV. |
| **Global Index** | Distributed like tables; supports scalability and efficient reads. |
| **Denormalization** | Stores redundant data for query optimization, moving join/filter logic to the server. |

## Creation
### Prerequisites
- Base table must exist in the same keyspace.
- MV name unique in keyspace.
- Must include **all** base table partition key columns in MV primary key.
- Optional: Include clustering columns and non-key columns.
- Cannot include static columns (unless partition key), collections, or undefined columns.

### Syntax
```cql
CREATE MATERIALIZED VIEW [IF NOT EXISTS] keyspace.mv_name AS
SELECT col1, col2, ..., *
FROM keyspace.base_table
WHERE pk_col1 IS NOT NULL AND pk_col2 IS NOT NULL AND ...  -- All PK columns required
PRIMARY KEY (new_pk_col1, new_ck_col1, ...);  -- New PK must start with base PK cols
```
- Use `IS NOT NULL` for all base PK columns in WHERE clause.
- PRIMARY KEY clause optional; inferred if omitted, but recommended for custom clustering.

### Examples
1. **Basic MV for querying by non-PK column**:
   ```cql
   CREATE TABLE cycling.events (
       event_date DATE,
       event_id TIMEUUID,
       event_name TEXT,
       location TEXT,
       PRIMARY KEY (event_date, event_id)
   );

   CREATE MATERIALIZED VIEW cycling.events_by_location AS
   SELECT event_id, event_date, event_name, location
   FROM cycling.events
   WHERE event_date IS NOT NULL AND event_id IS NOT NULL
   PRIMARY KEY ((location), event_date, event_id);  -- location as new partition key
   ```
   

2. **MV for email lookup** (from users table):
   ```cql
   CREATE MATERIALIZED VIEW mv_users_by_email AS
   SELECT email, user_id, name
   FROM users
   WHERE email IS NOT NULL AND user_id IS NOT NULL
   PRIMARY KEY ((email), user_id);
   ```
   

### Dropping
```cql
DROP MATERIALIZED VIEW [IF EXISTS] keyspace.mv_name;
```

## Usage
### Querying
Query MVs like regular tables; no joins needed. Use ALLOW FILTERING sparingly, as MVs optimize specific patterns.
```cql
SELECT * FROM keyspace.mv_name
WHERE new_pk_col = ? AND new_ck_col = ? ALLOW FILTERING;  -- If needed
```
- Example:
  ```cql
  SELECT * FROM cycling.events_by_location
  WHERE location = 'New York' AND event_date = '2023-01-01';
  ```
  

- Reads from MV are independent of base table; use appropriate consistency levels (e.g., QUORUM).

## Limitations and Restrictions
| Category | Details |
|----------|---------|
| **Key Restrictions** | - Must include all base PK columns.<br>- New PK must start with base PK (in any order).<br>- No static columns or collections in SELECT.<br>- No secondary indexes on MVs. |
| **Functional** | - Read-only; no direct DML.<br>- Cannot nest MVs (no MV on MV).<br>- One MV per base table per query pattern (but multiple MVs per base table allowed).<br>- No explicit refresh; always eventual consistency. |
| **Query** | - WHERE must match MV PK exactly; ALLOW FILTERING for non-PK.<br>- Cannot use base table columns not in MV SELECT. |
| **Other** | - Experimental in early Cassandra; stable in ScyllaDB.<br>- Limited to non-counter tables. |

## Best Practices
- **Design**: 
  - Create one MV per query pattern; include only queried columns to minimize storage.
  - Use for high-read, low-write workloads; avoid for write-heavy tables.
  - Denormalize judiciously—balance query speed vs. storage/write cost.
- **Optimization**:
  - Monitor with `nodetool cfstats` for MV storage/reads.
  - Pair with caching (e.g., Redis) for hot queries.
  - Use LSI for node-local queries, GSI for cross-node.
- **Maintenance**:
  - Drop unused MVs to reclaim space.
  - Test write latency impact during creation/load.
  - Ensure even data distribution via good partition keys.
- **When to Use**: For filtering on non-PK columns without full scans; alternative to app-level joins.

## Performance Implications
- **Storage**: Duplicates data; monitor disk usage (MVs are separate tables).
- **Writes**: Increased latency/amplification (base + MV updates); up to 2x for one MV.
- **Reads**: Faster for targeted queries (no scans/joins); same as base table speed.
- **Distribution**: MVs may span different nodes based on new PK, adding network hops.
- **Concurrency**: Handles read-before-write; eventual consistency tunable via coordinator.

Under the hood: On write, ScyllaDB replicates to MV synchronously. Reads hit MV directly. No joins—pure table access.

## Relation to Secondary Indexes
- **GSI/LSI**: Built on MVs; GSI for global queries (cross-node), LSI for local (same node as base).
- **vs. Traditional Indexes**: MVs allow custom PKs for better distribution; indexes are simpler but less flexible.
- **Creation**: Use `CREATE INDEX` for auto-MV generation, or manual MV for advanced control.
- **Filtering**: MVs enable efficient `WHERE` on indexed columns without ALLOW FILTERING penalties.

Example GSI via MV:
```cql
CREATE INDEX ON users (email);  -- Auto-creates MV under hood
```



## Additional Resources
- Official Docs: [Materialized Views](https://docs.scylladb.com/manual/stable/features/materialized-views.html)
- University: [Overview](https://university.scylladb.com/topic/materialized-views-overview-2/), [Under the Hood](https://university.scylladb.com/topic/materialized-views-under-the-hood/), [Indexes & Filtering](https://university.scylladb.com/courses/data-modeling/lessons/materialized-views-secondary-indexes-and-filtering/)
