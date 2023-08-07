/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
)

var nodename string

// clusterCmd represents the cluster command
var ClusterCmd = &cobra.Command{
	Use:   "cluster",
	Short: "Control your cluster",
	Long: `You can initialize your cluster 
add node to your cluster, remove node from your cluster and terminate cluster

Usage : vc cluster [command] [flag]
`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("cluster called")
	},
}

func init() {
	ClusterCmd.AddCommand(addCmd)
	ClusterCmd.AddCommand(deleteCmd)
	ClusterCmd.AddCommand(shellCmd)
	ClusterCmd.AddCommand(initCmd)
	ClusterCmd.AddCommand(terminateCmd)
}
