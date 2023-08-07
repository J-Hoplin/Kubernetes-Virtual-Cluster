/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"os"
)

var cfgFile string

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "virtual-cluster",
	Short: "Making a virtual Kubernetes Cluster",
	Long: `Making a virtual Kubernetes Cluster. 
Basically it build cluster based on multipass and K3S`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println(cfgFile)
	},
}

func init() {

}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
