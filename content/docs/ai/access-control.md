---
title: Control access
weight: 30
description: Use a JWT token to ensure that only authenticated and authorized users can access the LLM APIs.
---


With AI Gateway, you can use policies, such as JSON Web Tokens (JWT), to ensure that only authenticated users can access your LLM API. In addition, you can extract claims from the JWT to enforce fine-grained access control to particular APIs. For example, you can restrict access to certain APIs based on the user's role, group, organization, or any other claim within the JWT.

In the following example, you create a JWT provider with self-signed certificates and configure access to your LLM API by using the claims in the JWT. To verify that authentication works, you create JWTs for two different users, Alice and Bob. Alice's JWT contains the claims to successfully authenticate and authorize with AI Gateway. However, Bob's JWT is set up with an unsupported model name. Because of that, Bob's access to the LLM API is prohibited.

{{< callout type="info" >}}
You can optionally create other JWT tokens by using the [JWT generator tool](https://github.com/solo-io/solo-cop/blob/main/tools/jwt-generator/README.md). 
{{< /callout >}}

{{< callout type="warning" >}}
Use self-signed certificates for testing purposes only. In a production environment, you typically use a trusted Certificate Authority to sign the JWT tokens.
{{< /callout >}}

## Before you begin

1. [Set up AI Gateway](/docs/ai/setup/).
2. [Authenticate to your LLM provider](/docs/ai/auth/).

## Authenticate users with JWTs {#authenticate}

Enforce JWT authentication to your AI Gateway routes.

1. Create a VirtualHostOption resource to define an inline JWT provider. The JWT provider is used to validate the JWTs that are sent as part of the requests to the AI Gateway. In the following example, the JWT provider validates the JWT by using the public key that you add to the VirtualHostOption resource.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.solo.io/v1
   kind: VirtualHostOption
   metadata:
     name: jwt-provider
     namespace: gloo-system
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: ai-gateway
     options:
       jwt:
         providers:
           selfminted:
             issuer: solo.io
             jwks:
               local:
                 key: |
                   -----BEGIN PUBLIC KEY-----
                   MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAskFAGESgB22iOsGk/UgX
                   BXTmMtd8R0vphvZ4RkXySOIra/vsg1UKay6aESBoZzeLX3MbBp5laQenjaYJ3U8P
                   QLCcellbaiyUuE6+obPQVIa9GEJl37GQmZIMQj4y68KHZ4m2WbQVlZVIw/Uw52cw
                   eGtitLMztiTnsve0xtgdUzV0TaynaQrRW7REF+PtLWitnvp9evweOrzHhQiPLcdm
                   fxfxCbEJHa0LRyyYatCZETOeZgkOHlYSU0ziyMhHBqpDH1vzXrM573MQ5MtrKkWR
                   T4ZQKuEe0Acyd2GhRg9ZAxNqs/gbb8bukDPXv4JnFLtWZ/7EooKbUC/QBKhQYAsK
                   bQIDAQAB
                   -----END PUBLIC KEY-----
   EOF
   ```

2. Send a request to the AI API. Note that the request returns a 401 HTTP response code, because the JWT is missing in the request.
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H content-type:application/json -d '{
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "system",
          "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
        },
        {
          "role": "user",
          "content": "Compose a poem that explains the concept of recursion in programming."
        }
      ]
    }' | jq
   ```

   Example output:
   ```
   * Connected to XX.XXX.XX.XXX (XX.XXX.XX.XXX) port 8080 (#0)
   > POST /openai HTTP/1.1
   > Host: XX.XXX.XX.XXX:8080
   > User-Agent: curl/7.88.1
   > Accept: */*
   > content-type:application/json
   > Content-Length: 330
   > 
   } [330 bytes data]
   < HTTP/1.1 401 Unauthorized
   < www-authenticate: Bearer realm="http://XX.XXX.XX.XXX:8080/openai"
   < content-type: text/plain
   < date: Thu, 03 Oct 2024 14:59:51 GMT
   < server: envoy
   < transfer-encoding: chunked
   < 
   { [24 bytes data]
   100   344    0    14  100   330     81   1925 --:--:-- --:--:-- --:--:--  2072
   * Connection #0 to host XX.XXX.XX.XXX left intact
   ```

3. Save the JWT tokens for the users Alice and Bob in environment variables.
   1. Save the JWT token for Alice in an environment variable.
      ```sh
      export ALICE_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyAiaXNzIjogInNvbG8uaW8iLCAib3JnIjogInNvbG8uaW8iLCAic3ViIjogImFsaWNlIiwgInRlYW0iOiAiZGV2IiwgImxsbXMiOiB7ICJvcGVuYWkiOiBbICJncHQtMy41LXR1cmJvIiBdIH0gfQ.I7whTti0aDKxlILc5uLK9oo6TljGS6JUrjPVd6z1PxzucUa_cnuKkY0qj_wrkzyVN5djy4t2ggE1uBO8Llpwi-Ygru9hM84-1m53aO07JYFya1VTDsI25tCRG8rYhShDdAP5L935SIARta2QtHhrVcd1Ae7yfTDZ8G1DXLtjR2QelszCd2R8PioCQmqJ8PeKg4sURhu05GlBCZoXES9-rtPVbe6j3YLBTodJAvLHhyy3LgV_QbN7IiZ5qEywdKHoEF4D4aCUf_LqPp4NoqHXnGT4jLzWJEtZXHQ4sgRy_5T93NOLzWLdIjgMjGO_F0aVLwBzU-phykOVfcBPaMvetg
      ```

      Alice works in the `dev` team, and this token gives her access to the `gpt-3.5-turbo` model of the AI API:
      ```json
      {
        "iss": "solo.io",
        "org": "solo.io",
        "sub": "alice",
        "team": "dev",
        "llms": {
          "openai": [
            "gpt-3.5-turbo"
          ]
        }
      }
      ```

   2. Save the JWT token for Bob in an environment variable.
      ```sh
      export BOB_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyAiaXNzIjogInNvbG8uaW8iLCAib3JnIjogInNvbG8uaW8iLCAic3ViIjogImJvYiIsICJ0ZWFtIjogIm9wcyIsICJsbG1zIjogeyAibWlzdHJhbGFpIjogWyAibWlzdHJhbC1sYXJnZS1sYXRlc3QiIF0gfSB9.p7J2UFwnUJ6C7eXsFCSKb5b7ecWZ75JO4TUJHafjLv8jJ7GzKfJVk7ney19PYUrWrO4ntwnnK5_sY7yaLUBCJ3fv9pcoKyRtJTw1VMMTQsKkWFgvy-jEwc9M-D5lrUfR1HXGEUm6NBaj_Ja78XScPZb_-APPqMIvzDZU04vd6hna3UMc4DZE0wcnTjOqoND0GllHLupYTfgX0v9_AYJiKRAcJvol1W14dI7szpY5GFZtPqq0kl1g0sJPg-HQKwf7Cfvr_JLjkepNJ6A1lsrG8QbuUvMUAdaHzwLvF3L_G6VRjEte6okZpaq0g2urWpZgdNmPVN71Q_0WhyrJTr6SyQ
      ```

      Bob works in the `ops` team and does not have access to any LLM in the OpenAI. Instead, he has access to an LLM (`mistral-large-latest`) from a different AI provider (Mistral AI):
      ```json
      {
        "iss": "solo.io",
        "org": "solo.io",
        "sub": "bob",
        "team": "ops",
        "llms": {
          "mistralai": [
            "mistral-large-latest"
          ]
        }
      }
      ```


4. Repeat the request and include the JWT token for Alice in the `Authorization` header. Because Alice's JWT is successfully validated, access to the AI API is granted. Verify that the request succeeds with a 200 HTTP response code.
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H "Authorization: Bearer $ALICE_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
      }
    ]
   }' | jq
   ```

   Example output:
   ```json
   {
     "id": "chatcmpl-AEHdIbIIY5fRbeMwWlg30g086vPGp",
     "object": "chat.completion",
     "created": 1727967736,
     "model": "gpt-3.5-turbo-0125",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "In the realm of code, a concept unique,\nLies recursion, magic technique.\nA function that calls itself, a loop profound,\nUnraveling mysteries, in cycles bound.\n\nThrough countless calls, it travels deep,\nInto the realms of logic, where secrets keep.\nLike a mirror reflecting its own reflection,\nRecursion dives into its own inception.\n\nBase cases like roots in soil below,\nPreventing infinite loops that can grow,\nBreaking the chain of repetition's snare,\nGuiding the function with utmost care.\n\nA recursive dance, elegant and precise,\nSolving problems with coding advice.\nInfinite possibilities, layers untold,\nRecursion, a story waiting to unfold.",
           "refusal": null
         },
         ...
   ```

5. Repeat the request with Bob's JWT token and verify that the request succeeds, too.
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H "Authorization: Bearer $BOB_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
      }
    ]
   }' | jq
   ```

   Example output:
   ```json
   {
     "id": "chatcmpl-AEHePiN1oCFC9htOM4FVBj3H8Fbhq",
     "object": "chat.completion",
     "created": 1727967805,
     "model": "gpt-3.5-turbo-0125",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "In the realm of code, a dance so sublime,\nRecursion weaves a tale, weaving through time.\nA function calling itself, a loop that bends,\nA journey unfolding, with no clear ends.\n\nLike a mirror reflecting its own reflection,\nRecursion dives deep, without hesitation.\nEach step taken echoes the ones before,\nA pattern emerging, forevermore.\n\nIn its elegance lies a power untamed,\nSolving problems complex, never maimed.\nA nesting of calls, a puzzle in motion,\nRecursion's magic, a programmer's potion.\n\nYet tread carefully in this recursive land,\nFor infinite loops lie close at hand.\nBase cases guard against this wild fate,\nEnsuring recursion's journey is great.\n\nSo embrace this looping, this spiraling flight,\nIn the world of programming, recursion shines bright.\nA concept so profound, in code it weaves,\nA poetic dance, that truly achieves.",
           "refusal": null
         },
         ...
   ```

Requests from Alice and Bob succeed because both tokens can be validated with the public key of the local JWT provider in the JWT policy. To authorize access based on claims in the token, continue to the next section.

## Authorize access based on claims {#authorize}

Recall that the tokens for Alice and Bob have claims for teams and LLM model types. You can use the claims in the token to restrict access beyond basic authentication.

1. Create a RouteOption resource that extracts the `llms.openai` claim from the JWT. This claim represents the model the user has access to. The following example allows access to the AI API only if the JWT contains the `"llms.openai": "gpt-3.5-turbo"` claim.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.solo.io/v1
   kind: RouteOption
   metadata:
     name: openai-opt
     namespace: gloo-system
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: openai
     options:
       rbac:
         policies:
           viewer:
             nestedClaimDelimiter: .
             principals:
             - jwtPrincipal:
                 claims:
                   "llms.openai": "gpt-3.5-turbo"
                 matcher: LIST_CONTAINS
   EOF
   ```

2. Send another request to the AI API with the JWT token for Alice. Because the JWT matcher is set to `LIST_CONTAINS`, the request only succeeds if the `gpt-3.5-turbo` model is part of the claims that are extracted from the JWT token. Because Alice's JWT token includes that claim, the request succeeds.
   ```sh
   curl "$INGRESS_GW_ADDRESS:8080/openai" -H "Authorization: Bearer $ALICE_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
      }
    ]
   }' | jq
   ```

   Example output: 
   ```json
   {
     "id": "chatcmpl-AEHgemjsftwHaLao0pU6RX7Z1bLHB",
     "object": "chat.completion",
     "created": 1727967944,
     "model": "gpt-3.5-turbo-0125",
     "choices": [
       {
         "index": 0,
         "message": {
           "role": "assistant",
           "content": "In the realm of code, a mystical loop unfurled,\nWhere functions call themselves, a recursive world.\nLike a mirror reflecting into infinity,\nA recursive function repeats with divinity.\n\nIn this dance of elegance, a magic spell cast,\nEach iteration building upon the last.\nBreaking problems into smaller parts,\nRecursion delves into the depths of arts.\n\nWith each call, a journey deepens and grows,\nTackling complexities, the program flows.\nAn algorithmic waltz, a pattern sublime,\nRecursion weaves through space and time.\n\nBut beware the infinite loop, a dangerous fright,\nWithout a base case, endlessly in sight.\nYet with wisdom and care, the recursion will end,\nSolving problems with grace, a programmer's friend.\n\nSo embrace the recursive beauty, unfold and unfurl,\nIn the enchanted dance of the programming world.\nA poetic loop, a symphony of code,\nRecursion whispers secrets, a programmer's ode.",
           "refusal": null
         },
         ...
   ```

3. Send another request. This time, include the JWT token for Bob. Because Bob does not have access to that model, the request fails and a 403 HTTP response code is returned.
   ```sh
   curl -v "${INGRESS_GW_ADDRESS}:8080/openai" -H "Authorization: Bearer $BOB_TOKEN" -H content-type:application/json -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {             
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },                   
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
      }               
    ]              
   }' | jq
   ```

   Example output: 
   ```
   ...
   < HTTP/1.1 403 Forbidden
   < content-type: text/plain
   < date: Thu, 03 Oct 2024 15:06:58 GMT
   < server: envoy
   < transfer-encoding: chunked
   < 
   * Connection #0 to host XX.XXX.XX.XXX left intact
   RBAC: access denied
   ```

## Cleanup

Before you continue to the next tutorial, be sure to clean up the RouteOption resource that restricts Bob's access to the `gpt-3.5-turbo` model.

```sh
kubectl delete RouteOption openai-opt -n gloo-system
```

## Next

Great job! You learned how to use JWTs to authenticate and authorize users to your AI API. You can now add further protection to your LLM provider by setting up [rate limiting based on claims in a JWT token](/ai/tutorials/ratelimit/).

Note that if you do not want to complete the next tutorial and instead want to try a different tutorial, first clean up the JWT authentication resources that you created in these steps. If you do not remove the resources, you must include JWT tokens with the correct access in all subsequent curl requests to the AI API.

```sh
kubectl delete VirtualHostOption jwt-provider -n gloo-system
kubectl delete RouteOption openai-opt -n gloo-system
```