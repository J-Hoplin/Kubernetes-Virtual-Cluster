/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"errors"
	"github.com/spf13/cobra"
	"virtual-cluster/service/cluster"
)

// cluster/addCmd represents the cluster/add command
var addCmd = &cobra.Command{
	Use:   "add",
	Short: "Add node to your cluster",
	Long:  `Add node to your cluster`,
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		if value, flagErr := cmd.Flags().GetString("name"); flagErr != nil {
			err = flagErr
			return
		} else {
			if len(args) > 0 {
				err = errors.New("Unnecessary arguments found")
				return
			}
			err = cluster.AddNode(value)
		}
		return
	},
}

func init() {
	addCmd.Flags().StringVarP(&nodename, "name", "n", "", "Name of node you want to add to cluster. Name should exist in config file")
	addCmd.MarkFlagRequired("name")
}
