Here’s a **ScyllaDB 4.6 Cheatsheet** covering the most important commands, configurations, and tips you’ll need day-to-day.

ScyllaDB is a high-performance, NoSQL database that's API-compatible with Apache Cassandra. It is known for its "close-to-the-metal" architecture, which optimizes it for modern hardware.

---

# 🐍 ScyllaDB 4.6 Cheatsheet

## 🔹 Installation & Setup

```bash
# Start Scylla in Docker (single node)
docker run --name scylla -d scylladb/scylla:4.6 --smp 2 --memory 2G --overprovisioned 1

# Check logs
docker logs -f scylla
```

### Cluster (Docker Compose)

```yaml
version: '3'
services:
  scylla-node1:
    image: scylladb/scylla:4.6
    command: --smp 2 --memory 2G --overprovisioned 1 --alternator-port=8000
    ports:
      - "9042:9042"
      - "9180:9180"
      - "8000:8000"
```

---

## 🔹 Connecting

```bash
# CQL Shell (Cassandra Query Language)
cqlsh 127.0.0.1 9042

# REST API (Alternator - DynamoDB compatible)
curl http://127.0.0.1:8000
```

---

## 🔹 Keyspaces

```sql
-- Create keyspace (NetworkTopologyStrategy recommended for clusters)
CREATE KEYSPACE myks
WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 3};

-- List keyspaces
DESCRIBE KEYSPACES;

-- Drop keyspace
DROP KEYSPACE myks;
```

---

## 🔹 Tables

```sql
-- Create table
CREATE TABLE myks.users (
    user_id UUID PRIMARY KEY,
    name text,
    email text
);

-- Insert data
INSERT INTO myks.users (user_id, name, email)
VALUES (uuid(), 'Alice', 'alice@example.com');

-- Query data
SELECT * FROM myks.users;

-- Delete row
DELETE FROM myks.users WHERE user_id=<uuid>;

-- Drop table
DROP TABLE myks.users;
```

---

## 🔹 Useful Data Types

* `uuid` – unique ID
* `timeuuid` – time-based UUID
* `int`, `bigint`, `double`
* `text`, `varchar`
* `list<text>`, `set<int>`, `map<text,int>`
* `tuple<text,int>`

---

## 🔹 Indexing & Search

```sql
-- Secondary index
CREATE INDEX users_email_idx ON myks.users(email);

-- Materialized view
CREATE MATERIALIZED VIEW myks.users_by_email AS
    SELECT * FROM myks.users
    WHERE email IS NOT NULL
    PRIMARY KEY (email, user_id);
```

---

## 🔹 Cluster Management

```bash
# Node status
nodetool status

# Repair data
nodetool repair

# Compact SSTables
nodetool compact

# Cleanup unused data
nodetool cleanup

# Check info
nodetool info
```

---

## 🔹 Performance Tips

* Use **NetworkTopologyStrategy** for replication.
* Avoid `ALLOW FILTERING` in queries.
* Prefer **materialized views** or **secondary indexes** for queries on non-PK columns.
* Use **prepared statements** in applications.
* Scale by **adding nodes** → data auto-rebalances.

---

## 🔹 Backup & Restore

```bash
# Snapshot
nodetool snapshot myks

# List snapshots
nodetool listsnapshots

# Clear snapshots
nodetool clearsnapshot

# Restore: copy snapshot SSTables back into data dir, then restart node
```

---

## 🔹 Monitoring

* **Scylla Monitoring Stack** → Prometheus + Grafana.
* Exporter runs on `9180` by default.

```bash
curl http://127.0.0.1:9180/metrics
```

---

## 🔹 Alternator (DynamoDB API)

```bash
# Create table via AWS CLI
aws dynamodb create-table \
  --endpoint-url http://127.0.0.1:8000 \
  --table-name users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
```

---

⚡ **Tip:** ScyllaDB is fully Cassandra-compatible, but 10x faster due to its C++ core. Use `cqlsh` for CQL queries, `nodetool` for ops, and `alternator` for DynamoDB workloads.

