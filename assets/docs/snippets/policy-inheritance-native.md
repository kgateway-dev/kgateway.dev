Kubernetes Gateway API policies that can be defined on an HTTPRoute, such as timeouts and retries are inherited as follows: 

* Policies that are defined on a parent HTTPRoute are automatically inherited by all child or grandchild HTTPRoutes. 
* If the child or grandchild HTTPRoute defines a policy, this policy takes precedence and overrides the policy that is set on the parent. 