package cluster

import (
	"sync"
	"virtual-cluster/utility"
)

func TerminateCluster() (err error) {
	utility.ClearConsole()
	masterConfig, workerConfig, err := utility.GetMasterWorkerConfig()
	if err != nil {
		return err
	}
	totalTask := len(masterConfig) + len(workerConfig)
	endChannel := make(chan string)
	terminateChannel := make(chan any)

	wg := sync.WaitGroup{}
	wg.Add(totalTask + 1)

	go TerminateListener(totalTask, &wg, endChannel, terminateChannel)

	// Master node
	for k, v := range masterConfig {
		if ck := utility.CheckNodeNameExist(k); ck {
			go v.Terminate(k, endChannel)
		} else {
			// Do not create go routine if node not exist
			utility.CriticalMessage("Node name with '" + k + "' is not running!")
			wg.Done()
		}
	}

	// Worker node
	for k, v := range workerConfig {
		if ck := utility.CheckNodeNameExist(k); ck {
			go v.Terminate(k, endChannel)
		} else {
			// Do not create go routine if node not exist
			utility.CriticalMessage("Node name with '" + k + "' is not running!")
			wg.Done()
		}
	}
	wg.Wait()
	// Purge Multipass Instance
	utility.PurgeMultipassInstance()
	// Sync config file
	utility.InfoMessage("✨ Multipass instances purged!")
	if err := utility.SyncConfigFile(masterConfig, utility.MASTER_CONFIG); err != nil {
		utility.CriticalMessage("Fail to synchronize master node config - ", err.Error())
	}
	if err := utility.SyncConfigFile(workerConfig, utility.WORKER_CONFIG); err != nil {
		utility.CriticalMessage("Fail to synchronize worker node config - ", err.Error())
	}
	return nil
}

func TerminateListener(taskCount int, wg *sync.WaitGroup, end chan string, terminate chan any) {
	var counter int
	for {
		select {
		case node := <-end:
			counter += 1
			utility.InfoMessage("👋 Complete to terminate node - ", node)
			wg.Done()
			if counter == taskCount {
				go func() {
					terminate <- true
				}()
			}
		case <-terminate:
			utility.InfoMessage("✨ All of the node terminated! (Total ", taskCount, "nodes)")
			wg.Done()
			return
		}
	}
}
