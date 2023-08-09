/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"errors"
	"github.com/spf13/cobra"
)

// cluster/deleteCmd represents the cluster/delete command
var deleteCmd = &cobra.Command{
	Use:   "delete",
	Short: "Delete specific node from cluster",
	Long:  `Delete specific node from cluster`,
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		if len(args) > 0 {
			err = errors.New("Unnecessary arguments found")
			return
		}
	},
}

func init() {
	deleteCmd.Flags().StringVarP(&nodename, "name", "n", "", "Name of node you want to delete")
	addCmd.MarkFlagRequired("name")
}
