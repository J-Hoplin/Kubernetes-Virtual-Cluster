/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"errors"
	"github.com/spf13/cobra"
	"virtual-cluster/service/cluster"
)

// cluster/terminateCmd represents the cluster/terminate command
var terminateCmd = &cobra.Command{
	Use:   "terminate",
	Short: "Terminate specific node from cluster",
	Long:  `Terminate specific node from cluster.Flag or arguments not required and ignored`,
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		if len(args) > 0 {
			err = errors.New("Unnecessary arguments found")
			return
		}
		err = cluster.TerminateCluster()
		return
	},
}

func init() {

}
