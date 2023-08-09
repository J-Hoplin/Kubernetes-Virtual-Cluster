package utility

import (
	"encoding/json"
	"errors"
	"io"
	"os"
	"strings"
	"sync"
)

const (
	MASTER_NODE = "master"
	WORKER_NODE = "worker"
)

type MasterConfig struct {
	Cpu    string `json:"cpu"`
	Memory string `json:"memory"`
	Disk   string `json:"disk"`
	Ip     string `json:"ip"`
	Token  string `json:"token"`
}

type WorkerConfig struct {
	Cpu    string `json:"cpu"`
	Memory string `json:"memory"`
	Disk   string `json:"disk"`
	Ip     string `json:"ip"`
}

type WorkerJson map[string]*WorkerConfig

type MasterJson map[string]*MasterConfig

type ClusterNode interface {
	SyncIP(name string) (string, error)
	Terminate(name string, end chan string)
	CheckResourceAndReturnDefaultValue()
}

func (m *MasterConfig) Init(name string) error {
	if nameValidate := NodeNameValidater(name); !nameValidate {
		return errors.New("Node naming convention violated : " + name)
	}
	// Instance Check
	if exit := CheckNodeNameExist(name); exit {
		return errors.New("Node name '" + name + "' already running")
	}
	// Resource check and change to default value
	m.CheckResourceAndReturnDefaultValue()
	if version, err := GetK3SVersion(); err != nil {
		return err
	} else {
		cmd := GetCommandWithoutShown(SCRIPTS_PATH+"/nodeInit.sh", name, m.Cpu, m.Memory, m.Disk, MASTER_NODE, version)

		if initErr := cmd.Run(); initErr != nil {
			return initErr
		}
	}
	return nil
}

func (m *MasterConfig) Terminate(name string, end chan string) {
	_ = GetCommandWithoutShown(SCRIPTS_PATH+"/terminateCluster.sh", name).Run()
	// Clear ip, token info
	m.Ip = ""
	m.Token = ""
	end <- name
}

func (m *MasterConfig) SyncIP(name string) (string, error) {
	if result, err := GetPureCommand(SCRIPTS_PATH+"/getNodeIP.sh", name).Output(); err != nil {
		return "", err
	} else {
		m.Ip = strings.Trim(string(result), "\n")
		return m.Ip, err
	}
}

func (m *MasterConfig) SyncToken(name string) (string, error) {
	if result, err := GetPureCommand(SCRIPTS_PATH+"/getMasterToken.sh", name).Output(); err != nil {
		return "", err
	} else {
		m.Token = strings.Trim(string(result), "\n")
		return m.Token, err
	}
}

func (m *MasterConfig) CheckResourceAndReturnDefaultValue() {
	if m.Cpu == "" {
		m.Cpu = os.Getenv("MASTER_DEFAULT_CPU")
	}
	if m.Disk == "" {
		m.Cpu = os.Getenv("MASTER_DEFAULT_MEMORY")
	}
	if m.Disk == "" {
		m.Disk = os.Getenv("MASTER_DEFAULT_STORAGE")
	}
}

func (w *WorkerConfig) Init(name string, masterIp string, masterToken string, wg *sync.WaitGroup, res chan *NodeInitResult) {
	var result *NodeInitResult
	InfoMessage("🚀 Start initializing worker node : ", name)
	if nameValidate := NodeNameValidater(name); !nameValidate {
		result = &NodeInitResult{false, name, "Node naming convention violated : " + name}
	} else {
		if version, err := GetK3SVersion(); err != nil {
			result = &NodeInitResult{false, name, err.Error()}
		} else {
			// Check resource config and change to default value
			w.CheckResourceAndReturnDefaultValue()

			cmd := GetCommandWithoutShown(SCRIPTS_PATH+"/nodeInit.sh", name, w.Cpu, w.Memory, w.Disk, WORKER_NODE, masterToken, masterIp, version)
			if initErr := cmd.Run(); initErr != nil {
				result = &NodeInitResult{false, name, initErr.Error()}
			} else {
				_, _ = w.SyncIP(name)
				result = &NodeInitResult{true, name, ""}
			}
		}
	}
	_, _ = w.SyncIP(name)
	wg.Done()
	res <- result
	return
}

func (m *WorkerConfig) Terminate(name string, end chan string) {
	_ = GetCommandWithoutShown(SCRIPTS_PATH+"/terminateCluster.sh", name).Run()
	// Clear IP
	m.Ip = ""
	end <- name
}

func (w *WorkerConfig) SyncIP(name string) (string, error) {
	if result, err := GetPureCommand(SCRIPTS_PATH+"/getNodeIP.sh", name).Output(); err != nil {
		return "", err
	} else {
		w.Ip = strings.Trim(string(result), "\n")
		return w.Ip, err
	}
}

func (w *WorkerConfig) Add(name string, masterIp string, masterToken string) (err error) {
	InfoMessage("🚀 Initializing node - ", name)
	w.CheckResourceAndReturnDefaultValue()
	err = GetCommandWithoutShown(SCRIPTS_PATH+"/nodeInit.sh", name, w.Cpu, w.Memory, w.Disk, WORKER_NODE, masterToken, masterIp).Run()
	_, _ = w.SyncIP(name)
	return
}

func (m *WorkerConfig) CheckResourceAndReturnDefaultValue() {
	if m.Cpu == "" {
		m.Cpu = os.Getenv("WORKER_DEFAULT_CPU")
	}
	if m.Memory == "" {
		m.Memory = os.Getenv("WORKER_DEFAULT_MEMORY")
	}
	if m.Disk == "" {
		m.Disk = os.Getenv("WORKER_DEFAULT_STORAGE")
	}
}

type NodeInitResult struct {
	Success  bool
	Nodename string
	Message  string
}

func Readfile(filePath string) (file []byte, err error) {
	var fInstance *os.File
	fInstance, err = os.Open(filePath)
	if err != nil {
		return
	}
	file, err = io.ReadAll(fInstance)
	return
}

func GetMasterConfig() (config MasterJson, err error) {
	var jsonByte []byte
	if jsonByte, err = Readfile(MASTER_CONFIG); err != nil {
		return
	}
	err = json.Unmarshal(jsonByte, &config)
	return
}

func GetWorkerConfig() (config WorkerJson, err error) {
	var jsonByte []byte
	if jsonByte, err = Readfile(WORKER_CONFIG); err != nil {
		return
	}
	err = json.Unmarshal(jsonByte, &config)
	return
}

func SyncConfigFile(config any, destination string) error {
	var err error
	var file []byte
	file, err = json.MarshalIndent(config, "", JSON_INDENT)
	err = os.WriteFile(destination, file, 0755)
	return err
}

func PurgeMultipassInstance() {
	_ = GetCommandWithoutShown(SCRIPTS_PATH + "/purgeInstance.sh").Run()
}
