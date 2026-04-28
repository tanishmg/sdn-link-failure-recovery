# SDN-Based Link Failure Detection and Recovery

## 📌 Overview

This project demonstrates Software Defined Networking (SDN) using the Ryu controller and Mininet. It focuses on detecting link failures and understanding dynamic path computation in a network.

---

## ⚙️ Technologies Used

* Ryu Controller
* Mininet
* OpenFlow 1.3
* NetworkX

---

## 🧠 Key Concepts

* SDN architecture (control plane & data plane separation)
* LLDP-based topology discovery
* Packet-In message handling
* Flow rule concept (OpenFlow)
* Dijkstra’s shortest path algorithm
* Link failure detection using topology events

---

## 🚀 Features

* Automatic topology discovery
* Detection of link failures
* Graph-based path computation
* Simulation of network using Mininet

---

## 🛠️ How to Run

### Start Controller

```bash
ryu-manager --observe-links controller.py
```

### Start Mininet

```bash
sudo mn --topo linear,3 \
--controller=remote,ip=127.0.0.1,port=6633 \
--switch ovs,protocols=OpenFlow13
```

### Test Connectivity

```bash
pingall
```

### Simulate Link Failure

```bash
link s1 s2 down
```

---

## 🔍 Explanation

The controller builds a network graph using NetworkX. It learns host locations using Packet-In events and computes shortest paths between nodes. When a link fails, the controller updates the topology and recomputes the path.

---

## 📊 Outcome

* Demonstrated SDN working with centralized control
* Simulated link failure scenario
* Implemented dynamic routing logic conceptually

---

## 👤 Author

Tanish Mahadev Gupta
