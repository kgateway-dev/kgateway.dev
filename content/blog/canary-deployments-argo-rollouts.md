---
title: Canary Deployments with kgateway and Argo Rollouts
toc: false
publishDate: 2025-04-01T00:00:00-00:00
author: Brian Jimerson
excludeSearch: true
---

# Introduction

A canary deployment is a technique that allows teams to release a new version of software to a subset of consumers (people or other software) in a safe manner. Gradually, more consumers are moved to the latest version of the software until eventually all consumers are using the new version, at which point the old version can be retired.

Canary deployments reduce the risk of releasing new software by testing it with a small group of consumers while continuing to run the stable version for the majority. This allows teams to quickly and safely roll back if issues are found, without impacting the entire consumer base.

Canary deployments are accomplished by deploying the new software version alongside the stable version and splitting the traffic between them. The percentage of traffic to the new version is initially very small; it is gradually increased over time to send more and more consumers to the new version. How the traffic is split and what the promotion and rollback criteria are is up to the software delivery team. The important thing is that the new version can be tested in a safe, incremental manner as load increases until it is considered stable and ready for full promotion.

This technique is akin to the deployment's namesake: coal miners often sent canaries into mines before entering themselves. Canaries are very sensitive to poisonous gases that can be present in mines. If the canary didn't show signs of distress, the miners could assume it was safe to enter---or at least that gas levels were not immediately dangerous.

A simple canary deployment might look like this:

{{< reuse-image src="blog/canary-deployments-argo-rollouts-1.png" width="750px" >}}

[Argo Rollouts](https://argoproj.github.io/argo-rollouts/) is a very popular tool for performing canary deployments in Kubernetes environments. According to the Argo Rollouts website:

> *Argo Rollouts is a Kubernetes controller and set of CRDs that provides advanced deployment capabilities such as blue-green, canary, canary analysis, experimentation, and progressive delivery features to Kubernetes.*

Argo Rollouts can leverage many different ingress controllers and service meshes to shift traffic between versions of software, including [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/) implementations via the [Gateway API Plugin](https://github.com/argoproj-labs/rollouts-plugin-trafficrouter-gatewayapi/releases/). The Kubernetes Gateway API is an open, standard Kubernetes project to address routing in Kubernetes. [Kgateway](https://kgateway.dev/) is a [CNCF](https://www.cncf.io/) project that implements the Kubernetes Gateway API based on [Envoy proxy](https://www.envoyproxy.io/).

In this post and supporting documents, we will explore how you can use kgateway with Argo Rollouts to easily set up canary deployments for your software. We will use the reviews service that is part of the [Istio bookinfo sample application](https://istio.io/latest/docs/examples/bookinfo/) to demonstrate canary deployments with kgateway and Argo Rollouts.

The reviews service has 3 versions available to demonstrate traffic shaping in Istio. We will use it to demonstrate an Argo Rollout in action. We will create an Argo Rollout resource that initially deploys version 1 of the reviews service, then roll out version 2 and observe the progressive shift of traffic to it. Finally, version 2 will be promoted as the stable version.

The installation and configuration of kgateway, Argo Rollouts, and many of the Kubernetes objects are beyond the scope of this post. For a full set of instructions, there is a [companion lab](https://www.solo.io/resources/lab/understanding-kgateway-patterns-of-extensions) available.

# Argo Rollouts in Action

By using the Gateway API plugin, Argo Rollouts can leverage kgateway for shifting routes between application versions, as well as more advanced HTTP manipulation, such as header inspection.

First, we create 2 services: 1 for the stable version and 1 for the canary version. These names are arbitrary, and initially, they both have the same selector. Argo Rollouts will take care of managing selectors for us.

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: reviews-stable
  labels:
    app: reviews
    service: reviews
spec:
  ports:
  - port: 9080
    name: http
  selector:
    app: reviews
---
apiVersion: v1
kind: Service
metadata:
  name: reviews-canary
  labels:
    app: reviews
    service: reviews
spec:
  ports:
  - port: 9080
    name: http
  selector:
    app: reviews
```

Then, an HTTP Route is created that references both services. You don't need to worry about weights for the routes; Argo Rollouts takes care of that for us, too!

```yaml
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: bookinfo-reviews
spec:
  parentRefs:
  - name: http-gateway
  hostnames:
  - www.bookinfo.com
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /reviews
    backendRefs:
    - name: reviews-canary
      port: 9080
    - name: reviews-stable
      port: 9080
```

Finally, an Argo Rollout resource tells Argo how to control traffic to the services as it progresses through the deployment. 

Note that the Argo Rollout resource replaces the traditional Kubernetes Deployment resource. It will create and modify the necessary Kubernetes resources for you automatically.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: reviews-rollout
...
spec:
...
  strategy:
    canary:
      stableService: reviews-stable
      canaryService: reviews-canary
...
      plugins:
        argoproj-labs/gatewayAPI:
          httpRoutes:
          - name: bookinfo-reviews
            useHeaderRoutes: true
            namespace: default
      steps:
      - setCanaryScale:
          replicas: 1
...
      - pause: {}
      - setWeight: 10
      - pause: {duration: 10s}
      - setWeight: 20
      - pause: {duration: 10s}
      - setWeight: 40
      - pause: {duration: 10s}
      - setWeight: 60
      - pause: {duration: 10s}
      - setWeight: 100
...
```

The Rollout references the stable and canary services as the two services participating in the canary deployment. In the steps stanza, it creates one replica of the canary service, and gradually increases the weight of traffic to the canary service every 10 seconds.

You can view the status of the Rollout using the `argo kubectl` plugin, and see that 100% of the traffic is going to the stable version, since that is the only version deployed:

```yaml
kubectl argo rollouts get rollout reviews-rollout --watch
```

```yaml
Name:            reviews-rollout
Namespace:       default
Status:          ✔ Healthy
Strategy:        Canary
  Step:          12/12
  SetWeight:     100
  ActualWeight:  100
Images:          docker.io/istio/examples-bookinfo-reviews-v1:1.20.2 (stable)
Replicas:
  Desired:       1
  Current:       1
  Updated:       1
  Ready:         1
  Available:     1
NAME                                   KIND        STATUS     AGE    INFO
⟳ reviews-rollout                      Rollout     ✔ Healthy  48s    
└──# revision:1                                                      
   └──⧉ reviews-rollout-7d484c47b8     ReplicaSet  ✔ Healthy  48s    stable
      └──□ reviews-rollout-7d484c47b8-lhr5r  Pod        ✔ Running  48s    ready:1/1
```

And viewing the canary and stable services, you can see that Argo Rollouts updated the selector for the same pod:

```yaml
reviews-canary  ClusterIP  34.118.230.235  <none>  9080/TCP  4m41s  app=reviews,rollouts-pod-template-hash=7d484c47b8
reviews-stable  ClusterIP  34.118.230.94   <none>  9080/TCP  4m41s  app=reviews,rollouts-pod-template-hash=7d484c47b8
```

When we are ready to perform a canary deployment of our new version, we can easily use the `argo kubectl` plugin to update the image for the Rollout to version 2 (v2):

```yaml
kubectl argo rollouts set image reviews-rollout reviews=docker.io/istio/examples-bookinfo-reviews-v2:1.20.2
```

If we view the Rollout's status, we notice that the canary's status is paused. The canary is waiting for a person to tell it that it is OK to proceed with the rollout. We did this by setting the first pause step to empty, which tells Argo to wait for a manual approval before proceeding.

```yaml
Name:            reviews-rollout
Namespace:       default
Status:          ॥ Paused
Message:         CanaryPauseStep
Strategy:        Canary
  Step:          2/12
  SetWeight:     0
  ActualWeight:  0
Images:          docker.io/istio/examples-bookinfo-reviews-v1:1.20.2 (stable)
                 docker.io/istio/examples-bookinfo-reviews-v2:1.20.2 (canary)
Replicas:
  Desired:       1
  Current:       2
  Updated:       1
  Ready:         2
  Available:     2
NAME                                   KIND        STATUS     AGE    INFO
⟳ reviews-rollout                      Rollout     ॥ Paused   6m7s   
├──# revision:2                                                      
│  └──⧉ reviews-rollout-594c75879c     ReplicaSet  ✔ Healthy  14s    canary
│     └──□ reviews-rollout-594c75879c-t988z  Pod        ✔ Running  14s    ready:1/1
└──# revision:1                                                      
   └──⧉ reviews-rollout-7d484c47b8     ReplicaSet  ✔ Healthy  6m7s   stable
      └──□ reviews-rollout-7d484c47b8-lhr5r  Pod        ✔ Running  6m7s   ready:1/1
```

We should be able to test the new version before it's rolled out. To do this, we set a header route in the rollout; the header route uses the Gateway API plugin to inspect HTTP headers. If a request is received that has a header `role=qa`, that request will be sent to the canary version. So, while the rollout is paused, we can test the canary version simply by setting a header value.

We can continue the rollout by using the `argo kubectl` plugin again:

```yaml
kubectl argo rollouts promote reviews-rollout
```

And observe the rollout as it progresses, until 100% of the traffic is routed to the new version and it is promoted to be the stable version:

```yaml

Name:            reviews-rollout
Namespace:       default
Status:          ✔ Healthy
Strategy:        Canary
  Step:          12/12
  SetWeight:     100
  ActualWeight:  100
Images:          docker.io/istio/examples-bookinfo-reviews-v1:1.20.2
                 docker.io/istio/examples-bookinfo-reviews-v2:1.20.2 (stable)
Replicas:
  Desired:       1
  Current:       2
  Updated:       1
  Ready:         2
  Available:     2
NAME                                   KIND        STATUS     AGE    INFO
⟳ reviews-rollout                      Rollout     ✔ Healthy  3m2s   
├──# revision:2                                                      
│  └──⧉ reviews-rollout-5468ccc755     ReplicaSet  ✔ Healthy  115s   stable
│     └──□ reviews-rollout-5468ccc755-k8nkt  Pod        ✔ Running  114s   ready:1/1
└──# revision:1                                                      
   └──⧉ reviews-rollout-fb7dcdf44      ReplicaSet  ✔ Healthy  3m2s   delay:18s
      └──□ reviews-rollout-fb7dcdf44-8d7dn  Pod        ✔ Running  3m1s   ready:1/1
```

# Conclusion

In this post we have seen how Argo Rollouts and kgateway can enable teams to perform canary deployments of their software, drastically reducing the risk of releasing new software. This is a powerful example of how kgateway uses the standard Kubernetes Gateway API to allow tools such as Argo Rollouts to be highly interoperable.

For the full set of instructions and to see this in action for yourself, complete the [companion lab](https://www.solo.io/resources/lab/canary-releases-with-argo-rollouts-kgateway).