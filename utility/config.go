package utility

import (
	"errors"
	"os"
	"path/filepath"
)

var (
	DIR, err        = filepath.Abs(filepath.Dir(os.Args[0]))
	KUBE_CONFIG     = os.Getenv("HOME") + "/.kube/config"
	KUBE_CONFIG_DIR = os.Getenv("HOME") + "/.kube"
	MASTER_NODE_KEY = "master-node"
	MASTER_CONFIG   = "./nodes/master/config.json"
	WORKER_CONFIG   = "./nodes/worker/config.json"
	SCRIPTS_PATH    = "./scripts"
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
