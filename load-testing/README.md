# Load Agent using Locust

Locust is an open source load testing tool. Locust allows defining user behaviour with Python code, and swarming your system with millions of simultaneous users. 

## Setup VM to run 

```
apt-get update -y
apt-get upgrade -y
apt-get install -y docker.io git tmux htop sysstat iftop tcpdump
curl -SL https://github.com/docker/compose/releases/download/v2.7.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod a+x /usr/local/bin/docker-compose
 
cat << EOF > /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {"max-size": "10m", "max-file": "3"}
}
EOF
 
# Add swap file to add reliability to memory management...
dd if=/dev/zero of=/swap bs=1M count=512
chmod 0600 /swap
mkswap /swap
cat << EOF >> /etc/fstab
# add
/swap swap      swap    defaults        0 2
EOF

reboot
```

## Running load tests
```
git clone <the github repo>
cd afj-load
# A fork of AFJ is currently used to support listening to trustping events. This pull request was added to AFJ, and future versions may use the standard AFJ package.
git clone https://github.com/reflectivedevelopment/aries-framework-javascript.git
git checkout feature/add_trustping_events

# modify environment variables in docker-compose.yml to specify load test parameters
# MEDIATION_URL= add your mediation invitation url here
# LOCUST_MIN_WAIT=60 min time between pings
# LOCUST_MAX_WAIT=120 max time between pings

# Some tests require the issuer or verifier to talk directly to AFJ. A port and IP address are required for this. The ports and IP address must be available for the Issuer or Verifier to contact for the tests to work correctly. In the case that the test is using a mediator, the IP and address don't need to be publicly available, but they still need to be allocated for code simplification.

# AGENT_IP=172.16.49.18

# A port range is required since each AFJ agent requires its own port. The ports are in a pool and are acquired from the pool as needed. If the process runs out of ports during operation, it will hang causes locust to freeze. Allocating at least one IP address per locust user is required. All the ports are mapped in Docker, so the more ports that are mapped, the longer it will take to start the docker environment.

# START_PORT=10000
# END_PORT=12000

# More than one locust file can be specified at a time. Each locust User will be assigned to run one test. After the tests are defined, other locust commands could be added to the end of the LOCUST_FILES parameter.

# LOCUST_FILES=locustMediatorPing.py,locustIssue.py # Specifies which tests to run
# LOCUST_FILES=locustMediatorPing.py --master -P 8090

# The Issuer URL and HEADERS required to use the issuer
# ISSUER_URL=http://172.16.49.18:8150
# ISSUER_HEADERS={"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ3YWxsZXRfaWQiOiIwOWY5ZDAwNC02OTM0LTQyZDYtOGI4NC1jZTY4YmViYzRjYTUiLCJpYXQiOjE2NzY4NDExMTB9.pDQPjiYEAoDJf3044zbsHrSjijgS-yC8t-9ZiuC08x8"}

# The cred def, credential attributes, and schema used for issuer load testing.
# CRED_DEF=MjCTo55s4x1UWy2W2spuU2:3:CL:131358:default
# CRED_ATTR='[{"mime-type": "text/plain","name": "score","value": "test"}]'
# SCHEMA=MjCTo55s4x1UWy2W2spuU2:2:prefs:1.0

# The ledger to use for issuance and verification. Additional networks can be added to config.js
# LEDGER=candy

docker-compose build
docker-compose up

# open web browser to localhost:8089
# run tests
```

## Issuer configuration

Accept TAA

Register DID

Register Schema

{
  "attributes": [
    "score"
  ],
  "schema_name": "prefs",
  "schema_version": "1.0"
}

Register Cred Def

Add Cred Def and Schema to env

## Load Test Notes

The start rate for clients, when to high will, will cause the mediator to be overloaded. 
Starting at new clients of 0.4 for every second is a good starting point.

Since the load testing uses AFJ for the clients, it may require more resources to run the
load environment than other Locust based load testing frameworks.

## Multi machine load test

Multiple locust nodes can be run to distribute the load testing. In the case of running
multiple nodes, you need to ensure each node has the environment variables set.

The master node will need to have a port opened to listen to incoming workers.

```
locust --master -P 8090
locust --worker
locust --worker  --master-host 10.128.15.214
```

## locustfile.py

The locustfile.py controls the AFJ agent by sending commands via STDIN and STDOUT over the subprocess. For load testing there are several different type of load tests that we wanted to run, so we created a base class locustClient.py that controls the agent.js AFJ script.

This is done for two reasons.

- The ARIES Framework clients are known to throw uncaught exceptions or crash under some circumstances, such as timeouts
- AFJ is written in JavaScript, and does not have a Python integration at this time. Using a subprocess allows locust to call AFJ code.

There is some issues that arise from agents crashing. The locustfile code focuses on handling agent crashes and ensuring the agents are running for the ping requests.

### locustIssue.py

locustIssue.py is designed to test issuing credentials. 

### locustMediatorIssue.py

locustIssue.py is designed to test issuing credentials using a mediator.

### locustIssueMsg.py

locustIssueMsg.py is designed to test sending messages from the issuer to the AFJ Client.

### locustMediatorMsg.py

locustMediatorMsg.py is designed to test sending messages from the issuer to the AFJ Client using the mediator.

### locustMediatorPing.py

locustMediatorPing.py is designed to test the number of agents that can connect to a mediator. A ping will be sent to the mediator and return via the websocket connection to ensure the agent is still connected.

### locustLiveness.py

locustLiveness.py is designed to test the issuer's /status REST API Call.

## agent.js

The agent.js is an event based architecture. It has a readline loop that listens for incoming commands. Commands are json strings. Examples

```
{"cmd":"start"}
{"cmd":"ping_mediator"}
{"cmd":"shutdown"}
```

## System requirements

* An IP address and ports accessible to the Issuer or Verifier if running tests without a mediator
* Each AFJ agent requires approximately 52 - 100 MB of ram. So a 32 GB machine should be able to run approximately 550 Users assuming 4 GB of OS overhead.
* CPU usage will vary depending upon LOCUST_X_TIME and load test being run

### Memory Usage

Memory usage is more complicated than looking at top and using the RSS value.

Looking at the process status in linux we can see the following
```
cat /proc/15041/status

Name:   node
Umask:  0022
State:  S (sleeping)
Tgid:   15041
Ngid:   0
Pid:    15041
PPid:   14769
TracerPid:      0
Uid:    0       0       0       0
Gid:    0       0       0       0
FDSize: 64
Groups:  
NStgid: 15041   178
NSpid:  15041   178
NSpgid: 14769   1
NSsid:  14769   1
VmPeak: 12090960 kB
VmSize: 12023888 kB
VmLck:         0 kB
VmPin:         0 kB
VmHWM:    225704 kB
VmRSS:    100892 kB
RssAnon:           49280 kB
RssFile:           51612 kB
RssShmem:              0 kB
VmData:   173944 kB
VmStk:       132 kB
VmExe:     78112 kB
VmLib:     16852 kB
VmPTE:      2760 kB
VmSwap:        0 kB
HugetlbPages:          0 kB
CoreDumping:    0
THP_enabled:    1
Threads:        19
SigQ:   0/63948
SigPnd: 0000000000000000
ShdPnd: 0000000000000000
SigBlk: 0000000000000000
SigIgn: 0000000001001000
SigCgt: 0000000188004602
CapInh: 00000000a80425fb
CapPrm: 00000000a80425fb
CapEff: 00000000a80425fb
CapBnd: 00000000a80425fb
CapAmb: 0000000000000000
NoNewPrivs:     0
Seccomp:        2
Seccomp_filters:        1
Speculation_Store_Bypass:       thread force mitigated
Cpus_allowed:   f
Cpus_allowed_list:      0-3
Mems_allowed:   00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001
Mems_allowed_list:      0
voluntary_ctxt_switches:        1162
nonvoluntary_ctxt_switches:     644
```

Focusing on memory usage

```
RssAnon:           49280 kB
RssFile:           51612 kB
```

It can be seen that the process uses a unique 49280 kB, but since the RssFile can be shared between processes, only one copy of 51612 kB needs to reside in memory. This results in each process using around ~50 MB of ram with an additional ~50 MB shared with all the processes.
