/*
Copyright © 2023 Hoplin <jhoplin7259@gmail.com>
*/
package main

import (
	"github.com/joho/godotenv"
	"os"
	"virtual-cluster/utility"
)
import "virtual-cluster/cmd"

func main() {
	/**
	Check requirement satisfied
	*/
	requirement_err := utility.CheckRequirementsInstalled()
	if requirement_err != nil {
		utility.CriticalMessage(requirement_err)
		os.Exit(1)
	}
	/**
	Load dotenv
	*/
	envErr := godotenv.Load()
	if envErr != nil {
		utility.CriticalMessage("Application crushed :Fail to load .env file")
		os.Exit(1)
	}
	cmd.Execute()
}
