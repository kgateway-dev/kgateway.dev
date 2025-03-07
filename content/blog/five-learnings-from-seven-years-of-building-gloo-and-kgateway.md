---
title: Five Learnings from Seven Years of Building Gloo and kgateway
toc: false
publishDate: 2025-03-04T00:00:00-00:00
author: Lin Sun, & Yuval Kohavi
---

We started Gloo Open Source in 2018, reaching GA in early 2019. Since then, we have grown Gloo adoption to hundreds of paid customers and numerous open-source users. We truly believe Gloo Gateway is the most mature and widely deployed Envoy-based gateway available in the market. This belief led us to [donate Gloo Gateway to the CNCF](https://www.youtube.com/watch?v=psZi_T1np4U) as ‘kgateway’ at KubeCon NA 2024, further enriching the cloud native API gateway ecosystem. In this blog, we share five key learnings from the past seven years of building [Gloo](https://github.com/solo-io/gloo)/[kgateway](https://github.com/kgateway-dev/kgateway).

## Not Donate to CNCF Sooner

A few years ago, we advocated for donating Gloo to CNCF, considering it was already open source and the leading Kubernetes-native gateway. Our reasoning was simple: why not place it in a vendor-neutral foundation like CNCF? 

However, due to shifting priorities and the complexities of reorganizing a widely adopted codebase to make it vendor-neutral, we deferred the decision until KubeCon NA 2024. In hindsight, had we donated Gloo to CNCF earlier, we could have gained more momentum, attracted more contributors, and accelerated the project’s growth path to a CNCF graduated project.

## Support Every Possible Use Case

Initially, we attempted to cover every conceivable use case, trying to anticipate future needs. Instead of waiting for user feedback, we provided extensive APIs for various scenarios. We quickly learnt that most users did not want to understand or manage excessive configurations as it overwhelms them rather than helping. Plus, too many configuration options ofted created confusion and hindered usability.

This is a common learning across open-source projects. As Tim Hockin famously said, “Let us keep Kubernetes unfinished.” When implementing Kubernetes Gateway API support in Gloo and kgateway, we embraced this philosophy. We focused on core use cases defined by the standard Gateway API while providing custom extensions on top of it, striking a balance between standardization and flexibility.

### Expose Internal Proxy Custom Resources to Users

When we designed Gloo, we structured it with two types of pods: Gloo and Gateway. The Gloo pod served as the control plane, while the Gateway pod ran as a programmed Envoy proxy based on user’s declarative intention via Gloo custom resources. To support multiple APIs, we introduced an intermediate Proxy custom resource (CR), which was responsible for translating various user’s declarative intentions into Envoy’s xDS representation to program the Gateway pod.

{{< reuse-image src="blog/five-learnings-1.png" width="750px" >}}

While this worked well for small to medium-scale users, it introduced challenges at larger scales. The Proxy resource grew too large for etcd, leading to performance issues in serialization and deserialization. Our critical mistake was making the Proxy resource a user-facing API rather than keeping it strictly internal. This forced us to maintain backward compatibility indefinitely, adding complexity over time. For example, there are now 4–5 ways to add listeners to the Proxy resource. To prevent this issue in kgateway, we decided to keep the Proxy resource internal.

## Rethinking Control Plane Extensibility

When we started Gloo in 2018, Kubernetes had not yet won the container orchestration war, so we built an abstraction layer to support multiple environments like Nomad, Consul, and file-based configurations. While this seemed flexible, it introduced inefficiencies. Our translation model used a snapshot-based structure, where upstreams, routes, and listeners were processed as a single large list. This simplified translation logic but severely impacted performance—any small change requiring recalculating the entire snapshot.

Furthermore, all proprietary fields were bundled into one snapshot, which worked in a project like Gloo but was unsuitable for a vendor-neutral CNCF project. This forced us to rethink extensibility.

### Envoy Filters

Envoy’s architecture is highly extensible through custom filters, exposing Envoy filters as a user-facing API. However, allowing users to bring their own Envoy filters introduces potential breaking changes during upgrades. Additionally, serialization and deserialization between Gloo’s control plane and data plane for many resources introduced performance bottlenecks. At scale, very large Envoy filters exceeded etcd limits, forcing us to split filters to mitigate etcd-related problems. We learned that heavy calculations should be performed once, not repeatedly. Based on our experience, we decided against user-configurable Envoy filters in kgateway.

In kgateway, we design all of our user facing extensions based on Kubernetes CRD. Our extension model is “in-process” where a vendor can use the upstream kgateway project as a library and build custom plugins to extend it.  Plugin system calls functions from the kgateway library but it doesn’t act as final xDS representation. While this approach requires vendor’s more effort upfront, it eliminates runtime failures, ensures stability and performance.

### One Large CRD or many small CRDs?

Another challenge was deciding between many small CRDs or one large CRD. While this may seem like a UX issue, the implications go beyond that. When updating a resource, if it includes a newer EnvoyFilter, applying the changes atomically in Kubernetes becomes difficult.

For example, consider a VirtualService object and an EnvoyFilter that modifies it within a Kubernetes cluster. If both the VirtualService and EnvoyFilter are updated simultaneously, an issue may arise where the new EnvoyFilter applies to the updated VirtualService. If this results in an error, the Kubernetes validation webhook will reject the VirtualService update but still accept the EnvoyFilter. This inconsistency can leave the system in a broken state, applying an incorrect route policy.

We learned that anything requiring transactional consistency must be in the same CRD. In kgateway, we provide CRDs that allow users to extend routes via extensionRef to custom resources. Since we own these CRDs, we can maintain compatibility and resolve issues effectively.

### Label Selectors

Label selection proved another scaling challenge as we can’t index them. You may be wondering why this is not a problem for kubernetes? Kubernetes calculates label selections sporadically, but Gloo resolved all label selections simultaneously, leading to an O(N^2) scaling problem. In most recent Gloo, we avoided generic label selectors in hot paths like route delegation. Instead, we predefine label-based route delegation, enabling indexing for optimized label selection calculations.

## Leveraging Istio’s Control Plane

Four years ago, we explored using Istio’s control plane to manage Gloo’s gateway proxy. Given Istio’s adoption by major enterprises like eBay and Airbnb, we expected it to handle large-scale environments effectively. Unifying control planes for mesh and gateway seemed like a natural simplification.

{{< reuse-image src="blog/five-learnings-2.png" width="500px" >}}

However, Istio lacked features we needed, leading us to implement numerous Envoy filters—a decision that quickly proved problematic. To prevent users from encountering upgrade issues, we had to add complex workarounds in our code base. Additionally, we struggled with eventual consistency and large Envoy filter sizes.

Developing features for Istio required deep understanding of its internal representations, making customization difficult. Instead of forcing Istio to fit our needs, we designed [Istio in Ambient mode](http://ambientmesh.io) to be pluggable for waypoints, allowing users to choose a different waypoint proxy like Gloo/kgateway.

{{< reuse-image src="blog/five-learnings-3.png" width="750px" >}}

## Control Plane Scalability

We initially used Kubernetes [controller-runtime](https://github.com/kubernetes-sigs/controller-runtime) for dependency tracking but later discovered [krt](https://github.com/istio/istio/blob/master/pkg/kube/krt/README.md), which provides a framework for building declarative controllers. Krt solved exactly the problems we faced, eliminating the need for manual dependency tracking, indexing, and reconciliation logic.

When implementing the Kubernetes Gateway API in kgateway, we deal with numerous objects interacting through targetRefs and extensionRefs. Managing these references manually with controller-runtime proved cumbersome—it provides the capability but requires manual wiring of dependencies. This means manually creating indexes, queueing events, and triggering reconciliation. With a large number of dependencies, we encountered frequent issues related to dependency tracking and resolution. Krt solved these problems by handling dependency tracking automatically. Whenever a change occurs, only the relevant objects are retranslated instead of recalculating everything.

Previously, Gloo’s snapshot-based model processed routes, upstreams, and other resources in a single translation cycle, meaning any small change triggered a full recalculation. Krt improves scalability by separating Proxy, Service/Backend, and Pod translations, ensuring that only relevant components are reprocessed when changes occur. For example, when a Pod endpoint changes, it won’t trigger the translation of the Proxy. Recognizing these benefits, we built kgateway to be fully krt-based, leveraging its efficient dependency tracking and reconciliation.

{{< reuse-image src="blog/five-learnings-4.png" width="750px" >}}

## Join the kgateway Community

If any of these learnings resonate with you, join us in the [kgateway slack channel](https://kgateway.dev/slack/) and follow us on [LinkedIn](https://www.linkedin.com/company/kgateway/). We’ve also got some free technical content available for the community to learn more about kgateway including [free hands-on labs](https://kgateway.dev/resources/labs/), [videos](https://kgateway.dev/resources/videos/) and [blogs](https://kgateway.dev/blog/). If you’re keen to help grow kgateway you can also join us at [GitHub](https://github.com/kgateway-dev/kgateway).

You can also catch the team at [KubeCon + CloudNativeCon Europe](https://www.solo.io/events/solo-io-at-kubecon-cloudnativecon-europe-2025) in London from April 1-4 at the Solo.io booth if you are interested in discussing the project further. We’d love to hear your thoughts and collaborate to build highly usable and scalable cloud native projects together! 
