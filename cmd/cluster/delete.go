/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"errors"
	"github.com/spf13/cobra"
	"virtual-cluster/service/cluster"
)

// cluster/deleteCmd represents the cluster/delete command
var removeCmd = &cobra.Command{
	Use:   "remove",
	Short: "Delete specific node from cluster",
	Long:  `Delete specific node from cluster`,
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		if value, flagErr := cmd.Flags().GetString("name"); flagErr != nil {
			err = flagErr
			return
		} else {
			if len(args) > 0 {
				err = errors.New("Unnecessary arguments found")
				return
			}
			err = cluster.RemoveNode(value)
		}
		return
	},
}

func init() {
	removeCmd.Flags().StringVarP(&nodename, "name", "n", "", "Name of node you want to delete")
	addCmd.MarkFlagRequired("name")
}
