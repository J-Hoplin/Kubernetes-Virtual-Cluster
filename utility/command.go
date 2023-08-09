package utility

import (
	"bytes"
	"os"
	"os/exec"
)

func GetCommand(commandString ...string) (cmd *exec.Cmd) {
	cmd = exec.Command(GetShellRuntime(), commandString...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin
	return
}

func GetCommandWithoutShown(commandString ...string) (cmd *exec.Cmd) {
	cmd = exec.Command(GetShellRuntime(), commandString...)
	var t bytes.Buffer
	cmd.Stdout = &t
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin
	return
}

func GetPureCommand(commandString ...string) (cmd *exec.Cmd) {
	cmd = exec.Command(GetShellRuntime(), commandString...)
	return
}
