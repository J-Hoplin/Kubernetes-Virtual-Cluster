/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"os"
	cmd "virtual-cluster/cmd/cluster"
	"virtual-cluster/utility"

	"github.com/spf13/cobra"
)

var (
	cfgFile string
	RootCmd = &cobra.Command{
		Use:   "vc",
		Short: "Making a virtual Kubernetes Cluster",
		Long: utility.InfoMessageString(`Making a virtual Kubernetes Cluster. 
It build cluster based on multipass and K3S`),
		Run: func(cmd *cobra.Command, args []string) {
			os.Exit(0)
		},
		RunE: func(cmd *cobra.Command, args []string) error {
			cmd.Help()
			return nil
		},
	}
)

func init() {
	RootCmd.AddCommand(cmd.ClusterCmd)
	/**
	Check required directory exist
	*/
	for _, v := range []string{utility.NODE_CONFIG_PATH, utility.SCRIPTS_PATH} {
		if x := utility.CheckFileOrDirectoryExist(v); !x {
			utility.CriticalMessage("Required directory not found : ", v)
			os.Exit(1)
		}
	}
}

func Execute() {
	RootCmd.Execute()
}
