package cluster

import (
	"errors"
	"virtual-cluster/utility"
)

func ConnectToNodeShell(name string) (err error) {
	// Check if it's proper name
	if validate := utility.NodeNameValidater(name); !validate {
		err = errors.New("Node naming convention violated : " + name)
		return
	}

	if validate := utility.CheckNodeNameExist(name); !validate {
		err = errors.New(utility.CriticalMessageString("Node name not found : ", name))
		return
	}

	if _, _, err = utility.GetMasterWorkerConfig(); err != nil {
		return errors.New(utility.CriticalMessageString("'", name, "' is not a kubernetes cluster instance"))
	}

	cmd := utility.GetCommand(utility.SCRIPTS_PATH+"/connectShell.sh", name)
	_ = cmd.Run()
	return nil
}
