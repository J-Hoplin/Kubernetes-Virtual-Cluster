package cluster

import (
	"virtual-cluster/utility"
)

func ConnectToNodeShell(name string) {
	cmd := utility.GetCommand(utility.SCRIPTS_PATH+"/connectShell.sh", name)
	_ = cmd.Run()
	return
}
