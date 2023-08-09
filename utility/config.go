package utility

import (
	"errors"
	"os"
	"path/filepath"
)

var (
	DIR, err         = filepath.Abs(filepath.Dir(os.Args[0]))
	KUBE_CONFIG      = os.Getenv("HOME") + "/.kube/config"
	KUBE_CONFIG_DIR  = os.Getenv("HOME") + "/.kube"
	MASTER_NODE_KEY  = "master-node"
	MASTER_CONFIG    = "./nodes/master/config.json"
	WORKER_CONFIG    = "./nodes/worker/config.json"
	SCRIPTS_PATH     = "./scripts"
	NODE_CONFIG_PATH = "./nodes"
	JSON_INDENT      = "\t"
)

func GetShellRuntime() string {
	return os.Getenv("SHELL_TYPE")
}

func GetK3SVersion() (version string, err error) {
	version = os.Getenv("K3S_VERSION")
	// if version is invalid
	if version == "" {
		err = errors.New("K3S version not found. Please set K3S Version before initialize cluster")
	}
	return
}

func GetMasterWorkerConfig() (master MasterJson, worker WorkerJson, err error) {
	// Get master node, worker node config
	master, masterErr := GetMasterConfig()
	worker, workerErr := GetWorkerConfig()

	getMsg := func(tp string) string {
		return CriticalMessageString("Fail to parse" + tp + "file (Invalid format)")
	}
	// Check error while get config
	if masterErr != nil {
		err = errors.New(getMsg("master node"))
		return
	} else {
		if workerErr != nil {
			err = errors.New(CriticalMessageString(getMsg("worker node")))
			return
		}
	}
	return
}
