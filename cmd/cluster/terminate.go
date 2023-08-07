/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// cluster/terminateCmd represents the cluster/terminate command
var terminateCmd = &cobra.Command{
	Use:   "terminate",
	Short: "Terminate specific node from cluster",
	Long:  `Terminate specific node from cluster.Flag or arguments not required`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("cluster/terminate called")
	},
}

func init() {

}
