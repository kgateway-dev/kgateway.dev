---
title: Securing kgateway with the GitHub Secure Open Source Fund
toc: false
publishDate: 2026-02-18T10:00:00-00:00
author: Nina Polshakova, Mayowa Fajobi, Art Berger
excludeSearch: true
---

Earlier this year, [kgateway](https://github.com/kgateway-dev/kgateway) was selected to participate in the [GitHub Secure Open Source Fund](https://github.com/open-source/github-secure-open-source-fund), an initiative that provides maintainers with a three-week education sprint focused on the latest tooling, best practices, and strategies for securing open source software projects.

Being part of this program was both an honor and an opportunity. The GitHub Secure Open Source Fund provided expert insights, structured guidance, and a collaborative environment where we learned alongside other open source maintainers who share the same commitment to strengthening the security of the ecosystem.

## Building on a Strong Foundation

Kgateway is a Kubernetes-native ingress controller and next-generation API gateway that builds on top of the Envoy proxy and implements the Kubernetes Gateway API. As such, security has always been a priority for kgateway. As part of the CNCF ecosystem, we emphasize licensing clarity, community governance, and responsible disclosure practices.

One key takeaway from the program was that security isn’t just about detecting issues; it’s about building processes that make fixing them routine and predictable.

Before the program began, we had already put important foundations in place, especially to handle an influx of AI-generated contributions:

- Community standards, including an AI-generated code policy section.
- GitHub Copilot running automated reviews on pull requests. 

However, the Secure Open Source Fund helped us formalize, automate, and strengthen our approach in meaningful ways.

## What We Improved

The kgateway team improved security processes related to vulnerability reporting, code scanning, and repository hygiene.

### 🔐 Formalized Vulnerability Reporting

We created a [`SECURITY.md` file](https://github.com/kgateway-dev/kgateway/blob/main/SECURITY.md) that clearly documents how to report vulnerabilities and what contributors can expect from our disclosure process. Alongside this, we refined our security incident response documentation to ensure we have a well-defined and actionable response plan. For more information, see the [docs](https://kgateway.dev/docs/envoy/latest/reference/vulnerabilities/).

### 🔎 Enabled gosec as a Required Check

We activated [`gosec`](https://github.com/securego/gosec) static analysis scanning and made it a required check on every pull request. While enabling it, we:

- Fixed type conversion issues  
- Addressed file permission concerns  
- Cleaned up findings surfaced by the scanner  

For a project extending the Gateway API with Kubernetes custom resources using Kubebuilder, kgateway introduces new types like TrafficPolicy and GatewayParameters. Catching unsafe type conversions, invalid references, or misconfigured RBAC early is critical. Static analysis with gosec provides an additional layer of guardrails, complementing Kubebuilder’s CRD validation, before changes ever reach production clusters.

When `gosec` fails locally or in CI on a pull request, it prints the specific rule ID, affected file, and line number, and a brief explanation of the issue, so contributors can quickly identify and remediate the finding.

This not only improved the codebase immediately but also ensured future contributions meet a higher security bar.

### 🧹 Cleaned Up Repository Secrets

We audited and removed unused secrets in our repository environments, reducing risk and improving overall repository hygiene.

## Why This Matters

The GitHub Secure Open Source Fund does more than support individual projects; it strengthens the entire open-source ecosystem by investing in its security foundation.

For kgateway, this experience helped us:

- Formalize and document our security processes. 
- Automate enforcement of secure coding practices.
- Connect with other maintainers facing similar security challenges.
- Engage our community more transparently around security.

Security is not a one-time milestone, but rather an ongoing commitment. This program accelerated our progress and reinforced our dedication to building kgateway as a secure, reliable project for the community. Because many of our maintainers are also involved in other open source projects such as [agentgateway](https://github.com/agentgateway/agentgateway), we are also applying the lessons learned from this security initiative to other projects.

If you maintain an open source project, start small: add a `SECURITY.md` file, enable dependency scanning, and audit unused secrets. Small steps compound quickly. 

We are immensely grateful to GitHub and everyone involved in the Secure Open Source Fund for their support and expertise.

Thanks, all!

{{< cards >}}
{{< card link="https://github.blog/open-source/maintainers/securing-the-ai-software-supply-chain-security-results-across-67-open-source-projects/" icon="external-link" title="GitHub blog post" description="Learn more about the Secure Open Source Fund projects" >}}
{{< /cards >}}
