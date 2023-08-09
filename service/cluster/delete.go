package cluster

import (
	"errors"
	"virtual-cluster/utility"
)

func RemoveNode(name string) error {
	if name == utility.MASTER_NODE_KEY {
		return errors.New(utility.CriticalMessageString("Can't remove master node by alone"))
	}
	// Check name is valid convention
	if nameValidate := utility.NodeNameValidater(name); !nameValidate {
		return errors.New("Node naming convention violated : " + name)
	}

	// Find if node is running
	if validate := utility.CheckNodeNameExist(name); !validate {
		return errors.New(utility.CriticalMessageString("Node name with '", name, "' not found"))
	}

	// Get worker config and check if config set exist
	workerConfig, err := utility.GetWorkerConfig()
	if err != nil {
		return err
	}
	target, checkConfigExist := workerConfig[name]
	if !checkConfigExist {
		return errors.New(utility.CriticalMessageString("'", name, "' set not exist in worker node config file"))
	}

	utility.InfoMessage("✅ Complete to validate node's information - ", name)
	if err := target.Remove(name); err != nil {
		utility.CriticalMessage("😓 Failed to remove worker node : ", name, "(Reason : ", err.Error(), ")")
		return err
	}
	utility.InfoMessage("✨ Complete to remove worker node : ", name)

	// Sync config file
	if err := utility.SyncConfigFile(workerConfig, utility.WORKER_CONFIG); err != nil {
		utility.CriticalMessage("Fail to synchronize worker node config - ", err.Error())
	}
	return nil
}
