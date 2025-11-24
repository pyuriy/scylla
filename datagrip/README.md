DataGrip **doesn't officially list ScyllaDB as a directly supported database** type on its website, but you **can connect and work with ScyllaDB** by using the existing **Apache Cassandra** data source configuration.

---

## 🛠️ Connection Method

ScyllaDB is designed to be a drop-in replacement for Apache Cassandra, using the same **Cassandra Query Language (CQL)** and network protocol. Because of this compatibility, you can leverage DataGrip's built-in Cassandra support to connect to ScyllaDB.

### Steps to Connect (Using Cassandra Driver)

1.  In DataGrip, create a **new Data Source** connection.
2.  Select **Apache Cassandra** from the list of database types.
3.  Configure your connection details (Host, Port, Keyspace, and User/Password).
    * The **default port** for ScyllaDB is the same as Cassandra: **9042**.
4.  DataGrip will use the Apache Cassandra JDBC driver, which is compatible with the ScyllaDB CQL API.
5.  Click **Test Connection** to confirm the connection is successful.

### ScyllaDB-Specific Drivers

Some users have also had success by manually configuring a **user driver** and using a specific ScyllaDB-optimized JDBC driver (sometimes provided by third parties) for potentially better performance or feature support, though this is a manual setup not officially bundled with DataGrip.

---

## 🚀 Native Support Status

It's worth noting that the JetBrains team has **active feature requests** on their tracker (like DBE-18435 and DBE-24602) to add **native, explicit support** for ScyllaDB to the list of supported databases in DataGrip. This would likely involve:

* Adding ScyllaDB to the dropdown list on the Data Source creation dialog.
* Potentially optimizing the bundled driver and introspection for ScyllaDB's specific architecture.

For now, the **Cassandra connection method** is the standard and recommended workaround.
