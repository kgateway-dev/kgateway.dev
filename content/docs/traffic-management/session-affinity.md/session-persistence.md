---
title: Session persistence
weight: 30
---

Ensure that traffic from a client is always routed to the same backend instance for the duration of a session.

## About

HTTPRoutes support `sessionPersistence`, also known as "strong" session affinity or sticky sessions. Session persistence ensures that traffic is always routed to the same backend instance for the duration of the session, which can improve request latency and the user experience.

In session persistence, a client directly provides information, such as a header or a cookie, that the gateway proxy uses as a reference to direct traffic to a specific backend server. The persistent client request bypasses the proxy's load balancing algorithm and is routed directly to the backend that it previously established a session with.

### Session persistence versus session affinity

In session persistence, the backend service is encoded in a cookie and affinity can be maintained for as long as the backend service is available. This makes session persistence more reliable than [session affinity through consistent hashing](../consistent-hashing), or "weak" session affinity, in which affinity might be lost when a backend service is added or removed, or if the gateway proxy restarts.

However, note that session persistence and session affinity can functionally work together in your kgateway setup. If you define both session persistence and session affinity through consistent hashing, the gateway proxy makes the following routing decisions for incoming requests:
- If the request contains a session persistence identity in a cookie or header, route the request directly to the backend that it previously established a session with.
- If no session persistence identity is present, load balance the request according to the defined session affinity configuration, along with any [load balancing configuration](../loadbalancing).

For more information about session peristence, see the [Kubernetes Gateway API enhancement doc](https://gateway-api.sigs.k8s.io/geps/gep-1619/).

