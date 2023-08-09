/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"github.com/spf13/cobra"
)

var nodename string

// clusterCmd represents the cluster command
var ClusterCmd = &cobra.Command{
	Use:   "cluster",
	Short: "Control your cluster",
	Long: `Initialize your own multi-node cluster in your PC! 
add node to your cluster, remove node from your cluster and terminate cluster

Usage : vc cluster [command] [flag]
`,
	Run: func(cmd *cobra.Command, args []string) {
		_ = cmd.Help()
	},
}

func init() {
	ClusterCmd.AddCommand(addCmd)
	ClusterCmd.AddCommand(removeCmd)
	ClusterCmd.AddCommand(shellCmd)
	ClusterCmd.AddCommand(initCmd)
	ClusterCmd.AddCommand(terminateCmd)
}
