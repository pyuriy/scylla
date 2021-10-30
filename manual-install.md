# Scylla on Ubuntu 18 - manual installation

## OS preparation on Ubuntu:

### Installing sshd:

_apt update_

_apt install openssh-server_

_systemctl status ssh_

### Changing hostname:

_sudo hostnamectl_ _set-hostname ubuntu1_

### Edit /etc/hosts file and add all nodes of the cluster:

_yvp@ubuntu1:~$ cat /etc/hosts_

_127.0.0.1 localhost_

_192.168.2.200 ubuntu0_

_192.168.2.201 ubuntu1_

_192.168.2.202 ubuntu2_

_192.168.2.203 ubuntu3_

Changing IP address:

_root@ubuntu5:~# cat /etc/netplan/00-installer-config.yaml_

_# This is the network config written by &#39;subiquity&#39;_

_network:_

_ethernets:_

_enp0s3:_

_addresses:_

_- 192.168.2.205/24_

_gateway4: 192.168.2.1_

_nameservers:_

_addresses:_

_- 192.168.2.1_

_search: []_

_version: 2_

_root@ubuntu5:~#_

_root@ubuntu5:~# netplan apply_

_root@ubuntu5:~#_

### Disable auto-updates for OS:

_yvp@ubuntu1:~$ cat /etc/apt/apt.conf.d/20auto-upgrades_

_APT::Periodic::Update-Package-Lists &quot;0&quot;;_

_APT::Periodic::Download-Upgradeable-Packages &quot;0&quot;;_

_APT::Periodic::AutocleanInterval &quot;0&quot;;_

_APT::Periodic::Unattended-Upgrade &quot;0&quot;;_

### Disable GUI(X-Windows):

_sudo systemctl set-default multi-user.target_

## Installing Scylla:

_51 sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 5e08fbd8b5d6ec9c_

_53 sudo apt install curl_

_54 sudo curl -L --output /etc/apt/sources.list.d/scylla.list http://downloads.scylladb.com/deb/ubuntu/scylla-4.4-$(lsb\_release -s -c).list_

_55 sudo apt-get update_

_56 sudo apt-get install -y scylla_

_57 sudo apt-get update_

_58 sudo apt-get install -y openjdk-8-jre-headless_

_59 sudo update-java-alternatives --jre-headless -s java-1.8.0-openjdk-amd64_

_60 java -version_

## Configuring Scylla:

_sudo vi /etc/scylla/scylla.yaml_

…

_cluster\_name: &#39;Test Cluster&#39;_

…

_seed\_provider:_

_# Addresses of hosts that are deemed contact points._

_# Scylla nodes use this list of hosts to find each other and learn_

_# the topology of the ring. You must change this if you are running_

_# multiple nodes!_

_- class\_name: org.apache.cassandra.locator.SimpleSeedProvider_

_parameters:_

_# seeds is actually a comma-delimited list of addresses._

_# Ex: &quot;\&lt;ip1\&gt;,\&lt;ip2\&gt;,\&lt;ip3\&gt;&quot;_

_#- seeds: &quot;127.0.0.1&quot;_

_- seeds: &quot;192.168.2.201,192.168.2.202,192.168.2.203&quot;_

…

_listen\_address: ubuntu1_

…

_rpc\_address: ubuntu1_

…

_rpc\_interface: enp0s3_

…

_api\_address: 192.168.2.201_

_developer\_mode: true_

## Scylla setup:

_root@ubuntu3:~# scylla\_setup_

_Skip any of the following steps by answering &#39;no&#39;_

_Do you want to run check your kernel version?_

_Yes - runs a script to verify that the kernel for this instance qualifies to run Scylla. No - skips the kernel check._

_[YES/no]_

_Reading package lists... Done_

_Building dependency tree_

_Reading state information... Done_

_The following additional packages will be installed:_

_libreadline5_

_Suggested packages:_

_xfsdump attr quota_

_The following NEW packages will be installed:_

_libreadline5 xfsprogs_

_0 upgraded, 2 newly installed, 0 to remove and 506 not upgraded._

_Need to get 782 kB of archives._

_After this operation, 4,301 kB of additional disk space will be used._

_Get:1 http://us.archive.ubuntu.com/ubuntu bionic/main amd64 libreadline5 amd64 5.2+dfsg-3build1 [99.5 kB]_

_Get:2 http://us.archive.ubuntu.com/ubuntu bionic/main amd64 xfsprogs amd64 4.9.0+nmu1ubuntu2 [683 kB]_

_Fetched 782 kB in 0s (1,920 kB/s)_

_Selecting previously unselected package libreadline5:amd64._

_(Reading database ... 137253 files and directories currently installed.)_

_Preparing to unpack .../libreadline5\_5.2+dfsg-3build1\_amd64.deb ..._

_Unpacking libreadline5:amd64 (5.2+dfsg-3build1) ..._

_Selecting previously unselected package xfsprogs._

_Preparing to unpack .../xfsprogs\_4.9.0+nmu1ubuntu2\_amd64.deb ..._

_Unpacking xfsprogs (4.9.0+nmu1ubuntu2) ..._

_Processing triggers for libc-bin (2.27-3ubuntu1) ..._

_Processing triggers for man-db (2.8.3-2ubuntu0.1) ..._

_Setting up libreadline5:amd64 (5.2+dfsg-3build1) ..._

_Setting up xfsprogs (4.9.0+nmu1ubuntu2) ..._

_update-initramfs: deferring update (trigger activated)_

_Processing triggers for libc-bin (2.27-3ubuntu1) ..._

_Processing triggers for initramfs-tools (0.130ubuntu3.8) ..._

_update-initramfs: Generating /boot/initrd.img-5.0.0-23-generic_

_I: The initramfs will attempt to resume from /dev/sda3_

_I: (UUID=df4456d5-fd42-49cc-ba01-5fbf2fd87441)_

_I: Set the RESUME variable to override this._

_WARN 2021-10-14 22:36:32,186 [shard 0] iotune - Available space on filesystem at /var/tmp/mnt: 124 MB: is less than recommended: 10 GB_

_INFO 2021-10-14 22:36:32,186 [shard 0] iotune - /var/tmp/mnt passed sanity checks_

_This is a supported kernel version._

_Do you want to verify the ScyllaDB packages are installed?_

_Yes - runs a script to confirm that ScyllaDB is installed. No - skips the installation check._

_[YES/no]yes_

_Do you want the Scylla server service to automatically start when the Scylla node boots?_

_Yes - Scylla server service automatically starts on Scylla node boot. No - skips this step. Note you will have to start the Scylla Server service manually._

_[YES/no]yes_

_Created symlink /etc/systemd/system/multi-user.target.wants/scylla-server.service → /lib/systemd/system/scylla-server.service._

_Do you want to enable Scylla to check if there is a newer version of Scylla available?_

_Yes - start the Scylla-housekeeping service to check for a newer version. This check runs periodically. No - skips this step._

_[YES/no]no_

_Created symlink /etc/systemd/system/scylla-housekeeping-daily.timer → /dev/null._

_Created symlink /etc/systemd/system/scylla-housekeeping-restart.timer → /dev/null._

_You current Scylla release is 4.4.5 the latest minor release is 4.5.0 go to http://www.scylladb.com for upgrade instructions_

_Do you want to setup Network Time Protocol(NTP) to auto-synchronize the current time on the node?_

_Yes - enables time-synchronization. This keeps the correct time on the node. No - skips this step._

_[YES/no]yes_

_Reading package lists... Done_

_Building dependency tree_

_Reading state information... Done_

_ntp is already the newest version (1:4.2.8p10+dfsg-5ubuntu7.3)._

_ntp set to manually installed._

_The following NEW packages will be installed:_

_ntpdate_

_0 upgraded, 1 newly installed, 0 to remove and 506 not upgraded._

_Need to get 51.3 kB of archives._

_After this operation, 183 kB of additional disk space will be used._

_Get:1 http://us.archive.ubuntu.com/ubuntu bionic-updates/universe amd64 ntpdate amd64 1:4.2.8p10+dfsg-5ubuntu7.3 [51.3 kB]_

_Fetched 51.3 kB in 0s (386 kB/s)_

_Selecting previously unselected package ntpdate._

_(Reading database ... 137316 files and directories currently installed.)_

_Preparing to unpack .../ntpdate\_1%3a4.2.8p10+dfsg-5ubuntu7.3\_amd64.deb ..._

_Unpacking ntpdate (1:4.2.8p10+dfsg-5ubuntu7.3) ..._

_Setting up ntpdate (1:4.2.8p10+dfsg-5ubuntu7.3) ..._

_Processing triggers for man-db (2.8.3-2ubuntu0.1) ..._

_14 Oct 22:38:10 ntpdate[16651]: adjust time server 91.189.91.157 offset 0.004266 sec_

_Do you want to setup RAID0 and XFS?_

_It is recommended to use RAID0 and XFS for Scylla data. If you select yes, you will be prompted to choose the unmounted disks to use for Scylla data. Selected disks are formatted as part of the process._

_Yes - choose a disk/disks to format and setup for RAID0 and XFS. No - skip this step._

_[YES/no]no_

_Do you want to enable coredumps?_

_Yes - sets up coredump to allow a post-mortem analysis of the Scylla state just prior to a crash. No - skips this step._

_[YES/no]no_

_Do you want to setup a system-wide customized configuration for Scylla?_

_Yes - setup the sysconfig file. No - skips this step._

_[YES/no]_

_Do you want to enable Network Interface Card (NIC) and disk(s) optimization?_

_Yes - optimize the NIC queue and disks settings. Selecting Yes greatly improves performance. No - skip this step._

_[yes/NO]yes_

_The clocksource is the physical device that Linux uses to take time measurements. In most cases Linux chooses the fastest available clocksource device as long as it is accurate. In some situations, however, Linux errs in the side of caution and does not choose the fastest available clocksource despite it being accurate enough. If you know your hardwares fast clocksource is stable enough, choose &quot;yes&quot; here. The safest is the choose &quot;no&quot; (the default)_

_Yes - enforce clocksource setting. No - keep current configuration._

_[yes/NO]_

_Do you want IOTune to study your disks IO profile and adapt Scylla to it? (\*WARNING\* Saying NO here means the node will not boot in production mode unless you configure the I/O Subsystem manually!)_

_Yes - let iotune study my disk(s). Note that this action will take a few minutes. No - skip this step._

_[YES/no]_

_tuning /sys/devices/pci0000:00/0000:00:0d.0/ata3/host2/target2:0:0/2:0:0:0/block/sda/sda1_

_tuning /sys/devices/pci0000:00/0000:00:0d.0/ata3/host2/target2:0:0/2:0:0:0/block/sda_

_tuning: /sys/devices/pci0000:00/0000:00:0d.0/ata3/host2/target2:0:0/2:0:0:0/block/sda/queue/nomerges 2_

_tuning /sys/devices/pci0000:00/0000:00:0d.0/ata3/host2/target2:0:0/2:0:0:0/block/sda/sda1_

_tuning /sys/devices/pci0000:00/0000:00:0d.0/ata3/host2/target2:0:0/2:0:0:0/block/sda/sda1_

_tuning /sys/devices/pci0000:00/0000:00:0d.0/ata3/host2/target2:0:0/2:0:0:0/block/sda/sda1_

_INFO 2021-10-14 22:39:10,818 [shard 0] iotune - /var/lib/scylla/view\_hints passed sanity checks_

_WARN 2021-10-14 22:39:10,819 [shard 0] iotune - Scheduler for /sys/devices/pci0000:00/0000:00:0d.0/ata3/host2/target2:0:0/2:0:0:0/block/sda/queue/scheduler set to mq-deadline. It is recommend to set it to noop before evaluation so as not to skew the results._

_INFO 2021-10-14 22:39:10,819 [shard 0] iotune - Disk parameters: max\_iodepth=64 disks\_per\_array=1 minimum\_io\_size=512_

_Starting Evaluation. This may take a while..._

_Measuring sequential write bandwidth: 3971 MB/s_

_Measuring sequential read bandwidth: 7336 MB/s_

_Measuring random write IOPS: 1111 IOPS_

_Measuring random read IOPS: 44831 IOPS_

_Writing result to /etc/scylla.d/io\_properties.yaml_

_Writing result to /etc/scylla.d/io.conf_

_Do you want to enable node exporter to export Prometheus data from the node? Note that the Scylla monitoring stack uses this data_

_Yes - enable node exporter. No - skip this step._

_[YES/no]_

_Created symlink /etc/systemd/system/multi-user.target.wants/scylla-node-exporter.service → /lib/systemd/system/scylla-node-exporter.service._

_Do you want to set the CPU scaling governor to Performance level on boot?_

_Yes - sets the CPU scaling governor to performance level. No - skip this step._

_[YES/no]_

_This computer doesn&#39;t supported CPU scaling configuration._

_Do you want to enable fstrim service?_

_Yes - runs fstrim on your SSD. No - skip this step._

_[YES/no]no_

_Will Scylla be the only service on this host?_

_Answer yes to lock all memory to Scylla, to prevent swapout. Answer no to do nothing._

_[YES/no]_

_Do you want to configure rsyslog to send log to a remote repository?_

_Answer yes to setup rsyslog to a remote server, Answer no to do nothing._

_[YES/no]no_

_ScyllaDB setup finished._

_scylla\_setup accepts command line arguments as well! For easily provisioning in a similar environment than this, type:_

_scylla\_setup --no-raid-setup --nic enp0s3 --no-coredump-setup \_

_--io-setup 1 --no-version-check --no-fstrim-setup \_

_--no-rsyslog-setup_

_Also, to avoid the time-consuming I/O tuning you can add --no-io-setup and copy the contents of /etc/scylla.d/io\*_

_Only do that if you are moving the files into machines with the exact same hardware_

_root@ubuntu3:~#_

## Staring Scylla service:

_root@ubuntu1:~# systemctl status scylla-server.service_

● _scylla-server.service - Scylla Server_

_Loaded: loaded (/lib/systemd/system/scylla-server.service; enabled; vendor preset: enabled)_

_Drop-In: /etc/systemd/system/scylla-server.service.d_

└─_capabilities.conf, dependencies.conf, sysconfdir.conf_

_Active: failed (Result: exit-code) since Thu 2021-10-14 22:54:45 EDT; 17s ago_

_Process: 19121 ExecStopPost=/opt/scylladb/scripts/scylla\_stop (code=exited, status=0/SUCCESS)_

_Process: 19119 ExecStart=/usr/bin/scylla $SCYLLA\_ARGS $SEASTAR\_IO $DEV\_MODE $CPUSET $MEM\_CONF (code=exited, status=1/FAILURE)_

_Process: 19088 ExecStartPre=/opt/scylladb/scripts/scylla\_prepare (code=exited, status=0/SUCCESS)_

_Main PID: 19119 (code=exited, status=1/FAILURE)_

_Status: &quot;starting prometheus API server&quot;_

_Oct 14 22:54:03 ubuntu1 scylla[19119]: [shard 0] init - starting prometheus API server_

_Oct 14 22:54:03 ubuntu1 scylla[19119]: [shard 0] init - Bad configuration: invalid &#39;listen\_address&#39;: ubuntu1,localhost: std::system\_error (error C-Ares:11, ubuntu1,loca_

_Oct 14 22:54:03 ubuntu1 scylla[19119]: [shard 0] init - Shutting down prometheus API server_

_Oct 14 22:54:03 ubuntu1 scylla[19119]: [shard 0] init - Shutting down prometheus API server was successful_

_Oct 14 22:54:03 ubuntu1 scylla[19119]: [shard 0] init - Shutting down sighup_

_Oct 14 22:54:03 ubuntu1 scylla[19119]: [shard 0] init - Shutting down sighup was successful_

_Oct 14 22:54:03 ubuntu1 scylla[19119]: [shard 0] init - Startup failed: bad\_configuration\_error (std::exception)_

_Oct 14 22:54:45 ubuntu1 systemd[1]: scylla-server.service: Main process exited, code=exited, status=1/FAILURE_

_Oct 14 22:54:45 ubuntu1 systemd[1]: scylla-server.service: Failed with result &#39;exit-code&#39;._

_Oct 14 22:54:45 ubuntu1 systemd[1]: Failed to start Scylla Server._

_root@ubuntu1:~#_

## Checking Scylla service status:

_root@ubuntu1:~#_ _systemctl status scylla-server.service_

● _scylla-server.service - Scylla Server_

_Loaded: loaded (/lib/systemd/system/scylla-server.service; enabled; vendor preset: enabled)_

_Drop-In: /etc/systemd/system/scylla-server.service.d_

└─_capabilities.conf, dependencies.conf, sysconfdir.conf_

_Active: active (running) since Thu 2021-10-14 23:06:45 EDT; 25min ago_

_Process: 19228 ExecStopPost=/opt/scylladb/scripts/scylla\_stop (code=exited, status=0/SUCCESS)_

_Process: 19243 ExecStartPre=/opt/scylladb/scripts/scylla\_prepare (code=exited, status=0/SUCCESS)_

_Main PID: 19274 (scylla)_

_Status: &quot;serving&quot;_

_Tasks: 2 (limit: 4915)_

_CGroup: /scylla.slice/scylla-server.slice/scylla-server.service_

└─_19274 /usr/bin/scylla --log-to-syslog 1 --log-to-stdout 0 --default-log-level info --network-stack posix --io-properties-file=/etc/scylla.d/io\_properties.ya_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.columns cbfaad00-2d66-11ec-8cd6-000000000000] Compacting [/var/lib/scylla/data/syst_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.columns cbfaad00-2d66-11ec-8cd6-000000000000] Compacted 2 sstables to [/var/lib/scy_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.tables cbffb610-2d66-11ec-8cd6-000000000000] Compacting [/var/lib/scylla/data/syste_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.tables cbffb610-2d66-11ec-8cd6-000000000000] Compacted 2 sstables to [/var/lib/scyl_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.scylla\_tables cc035f90-2d66-11ec-8cd6-000000000000] Compacting [/var/lib/scylla/dat_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.scylla\_tables cc035f90-2d66-11ec-8cd6-000000000000] Compacted 2 sstables to [/var/l_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.keyspaces cc077e40-2d66-11ec-8cd6-000000000000] Compacting [/var/lib/scylla/data/sy_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.keyspaces cc077e40-2d66-11ec-8cd6-000000000000] Compacted 2 sstables to [/var/lib/s_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.dropped\_columns cc0ad9a0-2d66-11ec-8cd6-000000000000] Compacting [/var/lib/scylla/d_

_Oct 14 23:20:07 ubuntu1 scylla[19274]: [shard 0] compaction - [Compact system\_schema.dropped\_columns cc0ad9a0-2d66-11ec-8cd6-000000000000] Compacted 2 sstables to [/var_

_root@ubuntu1:~#_

Checking cluster nodes&#39; status:

_root@ubuntu2:~# nodetool status_

_Using /etc/scylla/scylla.yaml as the config file_

_Datacenter: datacenter1_

_=======================_

_Status=Up/Down_

_|/ State=Normal/Leaving/Joining/Moving_

_-- Address Load Tokens Owns Host ID Rack_

_DN 192.168.2.201 ? 256 ? 1fc2d961-add2-4415-8c4f-d7aa2f9a38b3 rack1_

_UN 192.168.2.202 244.04 KB 256 ? 94f1e254-1187-45dd-829d-501a9b565087 rack1_

_DN 192.168.2.203 ? 256 ? 585f3bb4-c292-472b-ad3b-cb941a3bba37 rack1_

_Note: Non-system keyspaces don&#39;t have the same replication settings, effective ownership information is meaningless_

_root@ubuntu2:~#_

# Working with and testing Scylla

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
