package utility

import (
	"encoding/json"
	"errors"
	"io"
	"os"
)

const (
	MASTER_NODE = "master"
	WORKER_NODE = "worker"
)

type ClusterNode interface {
	SyncIP(name string) (string, error)
}

type MasterConfig struct {
	Cpu    string `json:"cpu"`
	Memory string `json:"memory"`
	Disk   string `json:"disk"`
	Ip     string `json:"ip"`
	Token  string `json:"token"`
}

type MasterJson map[string]MasterConfig

func (m *MasterConfig) Init(name string) error {
	if nameValidate := NodeNameValidater(name); !nameValidate {
		return errors.New("Node naming convention violated : " + name)
	}
	if version, err := GetK3SVersion(); err != nil {
		return err
	} else {
		cmd := GetCommand(SCRIPTS_PATH+"/nodeInit.sh", name, m.Cpu, m.Memory, m.Disk, MASTER_NODE, version)
		if initErr := cmd.Run(); initErr != nil {
			return initErr
		}
	}
	return nil
}

func (m *MasterConfig) SyncIP(name string) (string, error) {
	if result, err := GetCommandWithoutShown(SCRIPTS_PATH+"/getNodeIP.sh", name).Output(); err != nil {
		return "", err
	} else {
		m.Ip = string(result)
		return m.Ip, err
	}
}

func (m *MasterConfig) GetToken(name string) (string, error) {
	if result, err := GetCommandWithoutShown(SCRIPTS_PATH+"/getMasterToken.sh", name).Output(); err != nil {
		return "", err
	} else {
		return string(result), err
	}
}

type WorkerConfig struct {
	Cpu    string `json:"cpu"`
	Memory string `json:"memory"`
	Disk   string `json:"disk"`
	Ip     string `json:"ip"`
}

type WorkerJson map[string]WorkerConfig

func (w *WorkerConfig) Init(name string, masterIp string, masterToken string) error {
	if nameValidate := NodeNameValidater(name); !nameValidate {
		return errors.New("Node naming convention violated : " + name)
	}
	if version, err := GetK3SVersion(); err != nil {
		return err
	} else {
		cmd := GetCommandWithoutShown(SCRIPTS_PATH+"/nodeInit.sh", name, w.Cpu, w.Memory, w.Disk, WORKER_NODE, masterToken, masterIp, version)
		if initErr := cmd.Run(); initErr != nil {
			return initErr
		}
	}
	return nil
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
	json.Unmarshal(jsonByte, &config)
	return
}

func GetWorkerConfig() (config WorkerJson, err error) {
	var jsonByte []byte
	if jsonByte, err = Readfile(WORKER_CONFIG); err != nil {
		return
	}
	json.Unmarshal(jsonByte, &config)
	return
}
