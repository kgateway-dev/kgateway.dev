---
title: Keycloak as an IdP
description: Use Keycloak as an identity provider for OAuth.
weight: 18
---

To use OAuth features such as access token validation or authorization codes, you must have an OpenID Connect (OIDC) compatible identity provider (IdP). 

This guide shows you how to set up Keycloak as an IdP that is local to your cluster. With this guide, you set up a sample realm with two users, as well as configure settings that you might use for future auth scenarios.

You can adapt these steps for your own local or cloud IdP.

## Install Keycloak {#install}

{{< reuse "conrefs/snippets/policies/ext_auth/keycloak-install.md" >}}

## Configure Keycloak {#configure}

{{< reuse "conrefs/snippets/policies/ext_auth/keycloak-configure.md" >}}

## Cleanup

{{< reuse "conrefs/snippets/cleanup.md" >}}

```
kubectl delete namespace keycloak
```