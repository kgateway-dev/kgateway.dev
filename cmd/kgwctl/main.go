package main

import (
    "context"
    "fmt"
    "os"

    "github.com/spf13/cobra"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

    "github.com/kgateway-dev/kgateway/v2/pkg/kube"
)

const version = "v0.1.0"

func printLine(cmd *cobra.Command, msg string) {
    fmt.Fprintln(cmd.OutOrStdout(), msg)
}

func main() {
    rootCmd := &cobra.Command{
        Use:   "kgwctl",
        Short: "kgwctl is the CLI for kgateway",
        Long:  "kgwctl is the command-line interface to interact with kgateway resources.",
        Run: func(cmd *cobra.Command, args []string) {
            _ = cmd.Help()
        },
    }

    // Version command
    versionCmd := &cobra.Command{
        Use:     "version",
        Short:   "Show kgwctl version",
        Example: "kgwctl version",
        Run: func(cmd *cobra.Command, args []string) {
            printLine(cmd, fmt.Sprintf("kgwctl %s", version))
        },
    }
    rootCmd.AddCommand(versionCmd)

    // Get command
    getCmd := &cobra.Command{
        Use:   "get",
        Short: "Get kgateway resources",
        Example: `kgwctl get
kgwctl get -n kube-system`,
        Run: func(cmd *cobra.Command, args []string) {
            ns, _ := cmd.Flags().GetString("namespace")

            client, err := kube.NewClient()
            if err != nil {
                printLine(cmd, fmt.Sprintf("error creating client: %v", err))
                return
            }

            pods, err := client.CoreV1().Pods(ns).List(context.TODO(), metav1.ListOptions{})
            if err != nil {
                printLine(cmd, fmt.Sprintf("error listing pods: %v", err))
                return
            }

            printLine(cmd, fmt.Sprintf("Pods in namespace '%s':", ns))

            if len(pods.Items) == 0 {
                printLine(cmd, fmt.Sprintf("No pods found in namespace '%s'", ns))
                printLine(cmd, "Tip: try 'kubectl kgw get -n kube-system'")
                return
            }

            for _, pod := range pods.Items {
                printLine(cmd, "- "+pod.Name)
            }
        },
    }
    getCmd.Flags().StringP("namespace", "n", "default", "Namespace to query")
    rootCmd.AddCommand(getCmd)

    // Completion command
    rootCmd.AddCommand(completionCmd(rootCmd))

    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

func completionCmd(rootCmd *cobra.Command) *cobra.Command {
    cmd := &cobra.Command{
        Use:   "completion",
        Short: "Generate shell completion scripts",
    }

    cmd.AddCommand(&cobra.Command{
        Use:   "bash",
        Short: "Generate bash completion script",
        Run: func(cmd *cobra.Command, args []string) {
            _ = rootCmd.GenBashCompletion(os.Stdout)
        },
    })

    cmd.AddCommand(&cobra.Command{
        Use:   "zsh",
        Short: "Generate zsh completion script",
        Run: func(cmd *cobra.Command, args []string) {
            _ = rootCmd.GenZshCompletion(os.Stdout)
        },
    })

    cmd.AddCommand(&cobra.Command{
        Use:   "fish",
        Short: "Generate fish completion script",
        Run: func(cmd *cobra.Command, args []string) {
            _ = rootCmd.GenFishCompletion(os.Stdout, true)
        },
    })

    cmd.AddCommand(&cobra.Command{
        Use:   "powershell",
        Short: "Generate powershell completion script",
        Run: func(cmd *cobra.Command, args []string) {
            _ = rootCmd.GenPowerShellCompletionWithDesc(os.Stdout)
        },
    })

    return cmd
}
