/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// cluster/deleteCmd represents the cluster/delete command
var deleteCmd = &cobra.Command{
	Use:   "delete",
	Short: "Delete specific node from cluster",
	Long:  `Delete specific node from cluster`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("cluster/delete called")
	},
}

func init() {
	deleteCmd.Flags().StringVarP(&nodename, "name", "n", "", "Name of node you want to delete")
	addCmd.MarkFlagRequired("name")
}
