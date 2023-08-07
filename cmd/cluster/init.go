/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"virtual-cluster/service/cluster"

	"github.com/spf13/cobra"
)

// cluster/initCmd represents the cluster/init command
var initCmd = &cobra.Command{
	Use:   "init",
	Short: "Initialize your cluster",
	Long:  `Initialize your cluster.Flag or arguments not required`,
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		err = cluster.InitializeCluster()
		return
	},
}

func init() {
}
