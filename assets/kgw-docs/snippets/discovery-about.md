Kgateway comes with a built-in service discovery feature that can scan the Kubernetes services and Functions in your cluster and automatically create kgateway Backend resources for them to facilitate routing and self-service. To have more control over the services you want to create Backends for, you can disable service discovery and instead create Backends manually. 

The following resources can be discovered automatically:

* Kubernetes Services
* AWS EC2 instances
* AWS Lambda Functions
* OpenAPI-based Functions
