Kubernetes Virtual Cluster Simulator
===
#### **Project's idea is inspired by [@Present Jay](https://github.com/PresentJay/lightweight-kubernetes-sandbox-cli)!** 
***
![img](./img/1.png)
**Virtual multi-node kubernetes cluster with Canoniacal Multipass!**
***
## Required Spec

**Standard under below is environment of 1 master & 2 worker node**

- OS : Linux / Mac OS X (**Windows not supported!**)
- CPU
  - Least : 4 Core CPUs
  - Stable : 8 Core CPUs or upper
- Memory
  - If your environment is 8GB of RAM : 1 master, 1 worker node is recommended
  - Least : 16 GB of RAM
  - Stable : 32 GB of RAM or upper
- Python3 : ver 3.8 upper
***
## Pre-Requisite

- Install Multipass
  - https://multipass.run
- Install kubectl
  - https://kubernetes.io/docs/tasks/tools/
***
## Commands

- Initialize cluster

  - Due to lack of computing resources, master / worker node not initialize properly sometimes. Please check computing resource before initiate cluster. (Usually occured in 8/16 GB RAM PC)

  ```
  python3 cluster.py -c init
  ```

- Terminate cluster

  ```
  python3 cluster.py -c terminate
  ```
- Add new worker-node to cluster (Scale-Out)
  - `-n` option is required when using `-c add` option
  ```
  python3 cluster.py -c add -n <new-node-name>
  ```
- Connect to node instance's shell
  - `-n` option is required when using `-c shell` option
  ```
  python3 cluster.py -c shell -n <node-name>
  ```
- Delete worker-node from cluster
  - **Warning : This option ignore daemonsets and delete local datas of node!**
  - `-n` option is required when using `-c delete` option
  ```
  python3 cluster.py -c delete -n <node-name>
  ```

***
## How to use?
### Cluster Node Configuration

**You need to recognize that both master/worker node config data should be object type.**

**Only one master node is available.** Master node's configuration
is located in [nodes/master/config.json](./nodes/master/config.json), and should have key called `master-node`

```json
{
    "master-node": {
        "cpu": "2",
        "memory": "2048M",
        "disk": "20G",
        "ip": "",
        "token": ""
    }
}
```
**No limitation of worker node count.** You can add worker node in [nodes/worker/config.json](./nodes/worker/config.json). Add with following format

```
{
  ...,


    "worker-node-name": {
        "cpu": "(ex : 1)",
        "memory": "(ex : 2048M)",
        "disk": "(ex : 20G)",
    }

  ...,
}
```
key of config data becomes, node instance's name.

Recommend to set at lease `1 cpu` and `2048M of RAM`, `15GB of disk` per node

### kubectl
When you initialize the cluster, the kubectl on the host pc is connected to the virtual cluster. The previous existing kubectl setting will be saved as `~/.kube/config_cp`.

Execute `kubectl get nodes` in host machine for check after initiate cluster!

![img](./img/2.png)

### Scale out worker node
You initialize cluster. But let's say that you want to add new worker node in cluster. You don't need to terminate and re initialize cluster. Just add worker node information in [worker node config](./nodes/worker/config.json) 

```
{
  ...,


    "scaled-out-cluster": {
        "cpu": "(ex : 1)",
        "memory": "(ex : 2048M)",
        "disk": "(ex : 20G)",
    }

  ...,
}
```
and use command under below
```
python3 cluster.py -c add -n <new-node-name>
```
***
## TODO List
- [ ] Polymorphism Support about helm chart
- [ ] Apply dashboard