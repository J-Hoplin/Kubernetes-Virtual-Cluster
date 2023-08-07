package cluster

import (
	"errors"
	"fmt"
	"virtual-cluster/utility"
)

func getNodeIp() {}

func InitializeCluster() error {
	// Clear console
	utility.ClearConsole()

	// Get master node, worker node config
	masterConfig, masterErr := utility.GetMasterConfig()
	_, workerErr := utility.GetWorkerConfig()

	// Check error while get config
	if masterErr != nil {
		return masterErr
	} else {
		if workerErr != nil {
			return workerErr
		}
	}
	// Master node key exist
	if _, ok := masterConfig[utility.MASTER_NODE_KEY]; !ok {
		return errors.New("Master node config not found. Key should be " + utility.MASTER_NODE_KEY)
	}
	utility.InfoMessage("Complete to load master/worker nodes config!")

	// Master Node
	utility.InfoMessage("Initializing master node...")
	masterNode := masterConfig[utility.MASTER_NODE_KEY]
	if masterNodeErr := masterNode.Init(utility.MASTER_NODE_KEY); masterNodeErr != nil {
		return masterNodeErr
	}

	masterIp, err := masterNode.SyncIP(utility.MASTER_NODE_KEY)
	fmt.Println(masterIp)
	fmt.Println(err)
	return nil
}
