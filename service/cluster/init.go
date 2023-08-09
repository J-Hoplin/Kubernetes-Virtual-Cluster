package cluster

import (
	"errors"
	"fmt"
	"os"
	"sync"
	"time"
	"virtual-cluster/utility"
)

func getNodeIp() {}

func InitializeCluster() error {
	// Clear console
	utility.ClearConsole()

	// Get master node, worker node config
	masterConfig, workerConfig, err := utility.GetMasterWorkerConfig()
	if err != nil {
		return err
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
	/**
	Sync token and ip of master node.

	If one of these gets failed, Unable to generate worker node
	*/
	masterIp, ipSyncErr := masterNode.SyncIP(utility.MASTER_NODE_KEY)
	if ipSyncErr != nil {
		return ipSyncErr
	}
	masterToken, tokenSyncErr := masterNode.SyncToken(utility.MASTER_NODE_KEY)
	if tokenSyncErr != nil {
		return tokenSyncErr
	}
	fmt.Println()
	utility.SpecialMessage("[[ Master node config values ]]")
	utility.SpecialMessage("📝 Master Node IP : ", masterIp)
	utility.SpecialMessage("📝 Master Node Token : ", masterToken)
	utility.InfoMessage("✨ Complete to build Master node")
	fmt.Println()
	// Go routine
	wg := sync.WaitGroup{}
	nodeInitResCh := make(chan *utility.NodeInitResult)
	terminate := make(chan bool)
	// Add wait grouo -> '+1' about listener
	wg.Add(len(workerConfig) + 1)

	go WorkerNodeListener(len(workerConfig), &wg, nodeInitResCh, terminate)
	for k, v := range workerConfig {
		go v.Init(k, masterIp, masterToken, &wg, nodeInitResCh)
	}
	wg.Wait()

	fmt.Println()
	utility.InfoMessage("Generating kubeconfig file as - ", utility.KUBE_CONFIG)
	/**
	If directory not exist, make directory
	*/
	if exist := utility.CheckFileOrDirectoryExist(utility.KUBE_CONFIG_DIR); !exist {
		// Mkdir의 두번째 매개변수에는 디렉토리의 권한이 들어가게 된다.
		_ = os.Mkdir(utility.KUBE_CONFIG_DIR, 0755)
	}
	if exist := utility.CheckFileOrDirectoryExist(utility.KUBE_CONFIG); !exist {
		_ = os.Rename(utility.KUBE_CONFIG, utility.KUBE_CONFIG_DIR+"/config_cp")
		utility.SpecialMessage("kubeconfig file exist before will be save as - ", utility.KUBE_CONFIG_DIR+"/config_cp")
	}
	if cmd := utility.GetCommandWithoutShown(utility.SCRIPTS_PATH+"/getKubeConfig.sh", utility.MASTER_NODE_KEY, masterIp, utility.KUBE_CONFIG).Run(); cmd != nil {
		utility.CriticalMessage("Fail to generate kubeconfig file. Please generate local kubeconfig manually. - ", cmd.Error())
	}
	utility.InfoMessage("kubeconfig file generated")

	/**
	Sync config file
	*/
	if err := utility.SyncConfigFile(masterConfig, utility.MASTER_CONFIG); err != nil {
		utility.CriticalMessage("Fail to synchronize master node config - ", err.Error())
	}
	if err := utility.SyncConfigFile(workerConfig, utility.WORKER_CONFIG); err != nil {
		utility.CriticalMessage("Fail to synchronize worker node config - ", err.Error())
	}
	utility.SpecialMessage("🚀 Cluster ready!")
	return nil
}

func WorkerNodeListener(nodecount int, wg *sync.WaitGroup, nodeInitResCh chan *utility.NodeInitResult, terminate chan bool) {
	time.Tick(10)
	var counter int
	var successNodeCounter int
	for {
		select {
		case res := <-nodeInitResCh:
			counter += 1
			if res.Success {
				successNodeCounter += 1
				utility.InfoMessage("Complete to build worker node : ", res.Nodename)
			} else {
				utility.CriticalMessage("Failed to build worker node : ", res.Nodename, "(Reason : ", res.Message, ")")
			}
			// If all of the node initialized, make an event to channel
			if counter == nodecount {
				/**
				Channel은 GoRoutine 간의 통신을 위한 수단이라는 본질을 잊지말자
				https://brownbears.tistory.com/315
				*/
				go func() {
					terminate <- true
				}()

			}
		case <-terminate:
			fmt.Println()
			utility.InfoMessage("⭕️ Success - ", successNodeCounter, "/", nodecount)
			utility.CriticalMessage("❌  Failed - ", nodecount-successNodeCounter, "/", nodecount)
			wg.Done()
			return
		}
	}
}
