---
title: About
weight: 10
description:
---

A retry is the number of times a request is retried if it fails. This setting can be useful to avoid your apps from failing if they are temporarily unavailable. With retries, calls are retried a certain number of times before they are considered failed. Retries can enhance your app's availability by making sure that calls don’t fail permanently because of transient problems, such as a temporarily overloaded service or network.

## Configuration options

You can configure retries by using a Kubernetes Gateway API-native configuration or a {{< reuse "docs/snippets/trafficpolicy.md" >}} as shown in the following table


| Type of timeout| Description | Configured via | Attach to | 
| -- | -- | -- | --- | 
| [Request retries]({{< link-hextra path="/resiliency/retry/retry/" >}}) | Specify the number of times and duration for the gateway to try a connection to an unresponsive backend service. | <ul><li>HTTPRoute</li><li>{{< reuse "docs/snippets/trafficpolicy.md" >}} </li></ul>| <ul><li>HTTPRoute</li><li>HTTPRoute rule</li><li>Gateway listener ({{< reuse "docs/snippets/trafficpolicy.md" >}} only)</li></ul> | 
| [Per-try timeout]({{< link-hextra path="/resiliency/retry/per-try-timeout/" >}}) | Set a shorter timeout for retries than the overall request timeout.  | <ul><li>HTTPRoute</li><li>{{< reuse "docs/snippets/trafficpolicy.md" >}} </li></ul>| <ul><li>HTTPRoute </li><li>HTTPRoute rule</li><li>Gateway listener ({{< reuse "docs/snippets/trafficpolicy.md" >}} only)</li></ul> | 

