package cluster

import (
	"errors"
	"virtual-cluster/utility"
)

func AddCluster(name string) error {

	// Check if multipass instance with same name is running
	// If invalid args given, return error
	if validate := utility.CheckNodeNameExist(name); validate {
		return errors.New(utility.CriticalMessageString("Node name with '", name, "' already running"))
	}

	masterConfig, workerConfig, err := utility.GetMasterWorkerConfig()
	if err != nil {
		return err
	}
	target, checkConfigExist := workerConfig[name]
	// Check config exist
	if !checkConfigExist {
		return errors.New(utility.CriticalMessageString("'", name, "' set not exist in worker node config file"))
	}

	// Check name is valid convention
	if nameValidate := utility.NodeNameValidater(name); !nameValidate {
		return errors.New("Node naming convention violated : " + name)
	}

	utility.InfoMessage("📦 Complete to load node's information - ", name)
	// If master node's token and ip is not an empty string
	master := masterConfig[utility.MASTER_NODE_KEY]
	if master.Ip == "" || master.Token == "" {
		return errors.New(utility.CriticalMessageString("Master node's token or ip is empty string! Integrity broken!"))
	}

	// Run add node
	if err := target.Add(name, master.Ip, master.Token); err != nil {
		utility.CriticalMessage("😓 Failed to build worker node : ", name, "(Reason : ", err.Error(), ")")
		return err
	}
	utility.InfoMessage("✨ Complete to build worker node : ", name)

	// Sync config file
	if err := utility.SyncConfigFile(workerConfig, utility.WORKER_CONFIG); err != nil {
		utility.CriticalMessage("Fail to synchronize worker node config - ", err.Error())
	}
	return nil
}
