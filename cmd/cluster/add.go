/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// cluster/addCmd represents the cluster/add command
var addCmd = &cobra.Command{
	Use:   "add",
	Short: "Add node to your cluster",
	Long:  `Add node to your cluster`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("cluster/add called")
	},
}

func init() {
	addCmd.Flags().StringVarP(&nodename, "name", "n", "", "Name of node you want to add to cluster. Name should exist in config file")
	addCmd.MarkFlagRequired("name")
}
