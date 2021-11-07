
# How to use

1. Make sure your hosts are availavle via ssh without a password

2. Edit scylla.yml.j2 file according tou your configuration

3. Add servers to the inventory file /etc/absible/hosts

4. Run the playbook: ansible-playbook i.yml -b


# Testing 


## Running cqlsh:

_root@ubuntu3:~# cqlsh ubuntu3 9042_

_Connected to Test Cluster at ubuntu3:9042._

_[cqlsh 5.0.1 | Cassandra 3.0.8 | CQL spec 3.3.1 | Native protocol v4]_

_Use HELP for help._

_cqlsh\&gt; show version;_

_[cqlsh 5.0.1 | Cassandra 3.0.8 | CQL spec 3.3.1 | Native protocol v4]_

_cqlsh\&gt; show host;_

_Connected to Test Cluster at ubuntu3:9042._

_cqlsh\&gt; exit;_

_root@ubuntu3:~#_

## Create keyspace and table, try it out:

_cqlsh\&gt; CREATE KEYSPACE newdb WITH REPLICATION = { &#39;class&#39; : &#39;SimpleStrategy&#39;, &#39;replication\_factor&#39; : 1 };_

_cqlsh\&gt; DESCRIBE KEYSPACES;_

_system\_schema system\_auth system system\_distributed newdb system\_traces_

_cqlsh\&gt; USE newdb;_

_cqlsh:newdb\&gt; CREATE TABLE emp (id int PRIMARY KEY, name text, year text);_

_cqlsh:newdb\&gt; DESCRIBE tables;_

_emp_

_cqlsh:newdb\&gt; DESC emp;_

_CREATE TABLE newdb.emp (_

_id int PRIMARY KEY,_

_name text,_

_year text_

_) WITH bloom\_filter\_fp\_chance = 0.01_

_AND caching = {&#39;keys&#39;: &#39;ALL&#39;, &#39;rows\_per\_partition&#39;: &#39;ALL&#39;}_

_AND comment = &#39;&#39;_

_AND compaction = {&#39;class&#39;: &#39;SizeTieredCompactionStrategy&#39;}_

_AND compression = {&#39;sstable\_compression&#39;: &#39;org.apache.cassandra.io.compress.LZ4Compressor&#39;}_

_AND crc\_check\_chance = 1.0_

_AND dclocal\_read\_repair\_chance = 0.0_

_AND default\_time\_to\_live = 0_

_AND gc\_grace\_seconds = 864000_

_AND max\_index\_interval = 2048_

_AND memtable\_flush\_period\_in\_ms = 0_

_AND min\_index\_interval = 128_

_AND read\_repair\_chance = 0.0_

_AND speculative\_retry = &#39;99.0PERCENTILE&#39;;_

_cqlsh:newdb\&gt;_

_cqlsh:newdb\&gt; INSERT INTO emp (id, name, year) VALUES (1, &#39;Krishna&#39;, &#39;2017&#39;);_

_cqlsh:newdb\&gt; INSERT INTO emp (id, name, year) VALUES (2, &#39;Chandra&#39;, &#39;2317&#39;);_

_cqlsh:newdb\&gt; SELECT \* FROM emp;_

_id | name | year_

_----+---------+------_

_1 | Krishna | 2017_

_2 | Chandra | 2317_

_(2 rows)_

_cqlsh:newdb\&gt; SELECT \* FROM emp WHERE id=2;_

_id | name | year_

_----+---------+------_

_2 | Chandra | 2317_

_(1 rows)_

_cqlsh:newdb\&gt; exit;_

_root@ubuntu3:~#_

# Resources:

[http://exabig.com/blog/2017/09/22/install-scylla-ubuntu-16-04/](http://exabig.com/blog/2017/09/22/install-scylla-ubuntu-16-04/)

[https://www.scylladb.com/download/?platform=ubuntu-18.04&amp;version=scylla-4.4#open-source](https://www.scylladb.com/download/?platform=ubuntu-18.04&amp;version=scylla-4.4#open-source)

Ansible playbooks:

[https://github.com/scylladb/scylla-ansible-roles/wiki/ansible-scylla-node:-Deploying-a-Scylla-cluster](https://github.com/scylladb/scylla-ansible-roles/wiki/ansible-scylla-node:-Deploying-a-Scylla-cluster)
