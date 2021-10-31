##How to use

1. Make sure your hosts are availavle via ssh without a password

2. Edit scylla.yml file according tou your configuration

3. Add servers to the inventory file /etc/absible/hosts

4. Run the playbook: ansible-playbook i.yml -b


 ## testing:
root@ubuntu5:~# nodetool status
Using /etc/scylla/scylla.yaml as the config file
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address    Load       Tokens       Owns    Host ID                               Rack
UN  127.0.0.1  175.22 KB  256          ?       ba9761c7-5afd-44f0-a406-8fd743027a64  rack1

Note: Non-system keyspaces don't have the same replication settings, effective ownership information is meaningless
root@ubuntu5:~# cqlsh
Connected to Test Cluster at 127.0.0.1:9042.
[cqlsh 5.0.1 | Cassandra 3.0.8 | CQL spec 3.3.1 | Native protocol v4]
Use HELP for help.
cqlsh> CREATE KEYSPACE newdb WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
cqlsh> DESCRIBE KEYSPACES;

system_schema  system_auth  system  system_distributed  newdb  system_traces

cqlsh> USE newdb;
cqlsh:newdb> CREATE TABLE emp (id int PRIMARY KEY, name text, year text);
cqlsh:newdb> DESCRIBE tables;

emp

cqlsh:newdb> DESC emp;

CREATE TABLE newdb.emp (
    id int PRIMARY KEY,
    name text,
    year text
) WITH bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'ALL'}
    AND comment = ''
    AND compaction = {'class': 'SizeTieredCompactionStrategy'}
    AND compression = {'sstable_compression': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND dclocal_read_repair_chance = 0.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair_chance = 0.0
    AND speculative_retry = '99.0PERCENTILE';

cqlsh:newdb> INSERT INTO emp (id, name, year) VALUES (1, 'Krishna', '2017');
cqlsh:newdb> INSERT INTO emp (id, name, year) VALUES (2, 'Chandra', '2317');
cqlsh:newdb> SELECT * FROM emp;

 id | name    | year
----+---------+------
  1 | Krishna | 2017
  2 | Chandra | 2317

(2 rows)
cqlsh:newdb> SELECT * FROM emp WHERE id=2;

 id | name    | year
----+---------+------
  2 | Chandra | 2317

(1 rows)
cqlsh:newdb> exit
root@ubuntu5:~#
