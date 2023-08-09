/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"errors"
	"github.com/spf13/cobra"
	"virtual-cluster/service/cluster"
)

// cluster/shellCmd represents the shell command
var shellCmd = &cobra.Command{
	Use:   "shell",
	Short: "Connect to shell of specific node.",
	Long:  `Connect to shell of specific node.`,
	RunE: func(cmd *cobra.Command, args []string) (err error) {
		if value, flagErr := cmd.Flags().GetString("name"); flagErr != nil {
			err = flagErr
			return
		} else {
			if len(args) > 0 {
				err = errors.New("Unnecessary arguments found")
				return
			}
			err = cluster.ConnectToNodeShell(value)
		}
		return
	},
}

func init() {
	shellCmd.Flags().StringVarP(&nodename, "name", "n", "", "Name of node you want to connect")
	addCmd.MarkFlagRequired("name")
}
