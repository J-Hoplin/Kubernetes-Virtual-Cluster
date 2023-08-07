package utility

import (
	"errors"
	"fmt"
	"os/exec"
	"regexp"
	"strings"
)

var (
	NodeNamePattern *regexp.Regexp
)

func init() {
	// Node name pattern
	compile, err := regexp.Compile("^[A-Za-z0-9][A-Za-z0-9-]*$")
	NodeNamePattern = compile

	if err != nil {
		panic(fmt.Sprintln("Unable to compile regular expression statement : ", err))
	}
}

func NodeNameValidater(name string) bool {
	return NodeNamePattern.MatchString(name)
}

func CheckRequirementsInstalled() error {
	msgBuilder := func(msg string) string {
		return fmt.Sprintf("'%s' may not installed or not enrolled in PATH", msg)
	}
	/*
		Check requirements on init
		- Multipass
		- Kubectl
		- Helm
	*/
	requirements := make(map[string]*exec.Cmd)
	requirements["multipass"] = exec.Command("multipass", "--help")
	requirements["kubectl"] = exec.Command("kubectl", "--help")
	requirements["helm"] = exec.Command("helm", "--help")
	for k, cmd := range requirements {
		if err := cmd.Run(); err != nil {
			return errors.New(msgBuilder(k))
		}
	}
	return nil
}

func CheckNodeNameExist(name string) bool {
	command := exec.Command("multipass", "list")
	output, _ := command.CombinedOutput()
	instanceList := strings.Split(string(output), "\n")[1:]
	for _, v := range instanceList {
		if filtered := strings.Split(v, " ")[0]; filtered == name {
			return true
		}
	}
	return false
}

func CheckMultipassInstanceIsClusterInstance(name string) bool {
	masters, _ := GetMasterConfig()
	workers, _ := GetWorkerConfig()
	// Able to check key exist with second return value
	_, masterCheck := masters[name]
	_, workerCheck := workers[name]
	return masterCheck || workerCheck
}
