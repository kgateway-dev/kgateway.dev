---
title: Visualize resource dependencies
weight: 15
description: Visualize the relationship and dependencies for all your kgateway and Kubernetes Gateway API resources in a DOT Graph. 
---

Visualize the relationship and dependencies for all your kgateway and Kubernetes Gateway API resources in a DOT Graph. 

## About DOT Graphs

A DOT graph is a plain text graph description language that is primarily used with [Graphviz](https://graphviz.org/). Graphviz is an open source graph visualization software to represent structural information and networks as diagrams, such as flowcharts, dependency trees, and state machines.

The kgwctl CLI has built-in support for generating DOT graphs to show the dependencies and relationships of kgateway and Kubernetes Gateway API resources.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Visualize your resources

1. Generate a graph for a particular resource in your cluster. The following command generates a graph for the http Gateway that you created in [before you begin](#before-you-begin)

   ```sh
   kgwctl get gateway http -n kgateway-system -o graph > output.graph
   ```

2. Open the [Graphviz online playground]( https://dreampuf.github.io/GraphvizOnline). 

3. Copy and paste the output of `output.graph` into the Graphviz online playground. The tool automatically generates the DOT graph for you. 

   {{< reuse-image src="img/graphviz.svg" >}}