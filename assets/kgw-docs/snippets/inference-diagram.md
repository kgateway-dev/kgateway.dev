```mermaid
graph LR
    Client -->|inference request| agentgateway
    agentgateway -->|routes to| InferencePool
    subgraph  
        subgraph InferencePool
            direction LR
            InferenceModel_v1
            InferenceModel_v2
            InferenceModel_v3
        end
        agentgateway
    end
```