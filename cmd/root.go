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
}

func Execute() {
	RootCmd.Execute()
}
