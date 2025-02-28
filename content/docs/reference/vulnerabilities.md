---
title: Security vulnerabilities
weight: 50
---

Review how the {{< reuse "docs/snippets/product-name.md" >}} project handles the lifecycle of Common Vulnerability and Exposures (CVEs).

## Reports

The {{< reuse "docs/snippets/product-name.md" >}} project appreciates the efforts of our users in helping us to discover and resolve security vulnerabilities. The following sources are used to determine product exposure to CVEs:

* The {{< reuse "docs/snippets/product-name.md" >}} team scans {{< reuse "docs/snippets/product-name.md" >}} components to detect vulnerabilities.
* The {{< reuse "docs/snippets/product-name.md" >}} team participates in early disclosure and security workgroups of multiple backend communities.
* Users may share output from their own security scanning tools for analysis and response from the {{< reuse "docs/snippets/product-name.md" >}} team.

### 📨 Where to report

To report a security vulnerability, email the private Google group `k8s-gateway-vulnerability-reports@googlegroups.com`.

### ✅ When to send a report

Send a report when:

* You discover that a {{< reuse "docs/snippets/product-name.md" >}} component has a potential security vulnerability.
* You are unsure whether or how a vulnerability affects {{< reuse "docs/snippets/product-name.md" >}}.

### 🔔 Check before sending

If in doubt, send a private message about potential vulnerabilities such as:

* Any crash, especially in Envoy.
* Any potential Denial of Service (DoS) attack.

### ❌ When NOT to send a report

Do not send a report for vulnerabilities that are not part of the {{< reuse "docs/snippets/product-name.md" >}} project, such as:

* You want help configuring {{< reuse "docs/snippets/product-name.md" >}} components for security purposes.
* You want help applying security related updates to your {{< reuse "docs/snippets/product-name.md" >}} configuration or environment.
* Your issue is not related to security vulnerabilities.
* Your issue is related to base image dependencies, such as Envoy.

## Evaluation

The {{< reuse "docs/snippets/product-name.md" >}} team evaluates vulnerability reports for:

* Severity level, which can affect the priority of the fix
* Impact of the vulnerability on {{< reuse "docs/snippets/product-name.md" >}} code as opposed to backend code
* Potential dependencies on third-party or backend code that might delay the remediation process

The {{< reuse "docs/snippets/product-name.md" >}} team strives to keep private any vulnerability information with us as part of the remediation process. We only share information on a need-to-know basis to address the issue.

## Remediation

Remediation of a CVE involves introducing a fix to the affected code and releasing the associated component. This development process might happen in private GitHub repositories to keep information secure and prevent broader exploitation of the vulnerability. 

## Disclosures

The {{< reuse "docs/snippets/product-name.md" >}} team discloses remediated vulnerabilities publicly. Additionally, you can join an early disclosure group to help address vulnerabilities earlier in the remediation process.

### Public disclosure

On the day for the remediation to be disclosed, the {{< reuse "docs/snippets/product-name.md" >}} team takes steps that might include the following:

* Merge changes from any private repositories into the public codebase
* Share security scan results for product images
* Publish a release and any corresponding documentation for mitigating the vulnerability
* Announce the remediated vulnerability in a public channel such as email or Slack

### Early disclosure

You can join a distribution list to get early disclosures of security vulnerability. This way, you can take action earlier in the process to help remediate the vulnerability and mitigate its effects in your environments.

To request membership in the early disclosure group, email the private Google group `k8s-gateway-vulnerability-reports@googlegroups.com`. In your request, indicate how you meet the following membership criteria.

#### Membership criteria

1. Contribute significantly to the {{< reuse "docs/snippets/product-name.md" >}} project, such as by being a maintainer, release manager, or active feature developer.
2. Use {{< reuse "docs/snippets/product-name.md" >}} in a way that justifies early disclosure of security vulnerabilities, such as redistributing {{< reuse "docs/snippets/product-name.md" >}} or providing {{< reuse "docs/snippets/product-name.md" >}} to many users outside your own organization.
3. Monitor the email that you provide for the early disclosure distribution list.
4. Participate in and attend meetings of the security working group.
5. Keep any information from the distribution list private and on a need-to-know basis. Information is only for purposes of remediating the vulnerability. If you share information beyond the scope of this policy, you must notify the distribution list, including details of what information was shared when and to whom, so the {{< reuse "docs/snippets/product-name.md" >}} team can assess how to proceed.

#### Membership removal

You must actively meet the membership criteria to remain part of the early disclosure distribution list. If your organization stops meeting one or more of these criteria, you can be removed from the distribution list.

#### Other membership notes

Membership in the [Envoy security group](https://github.com/envoyproxy/envoy/blob/main/SECURITY.md#security-reporting-process) is a separate process. Because {{< reuse "docs/snippets/product-name.md" >}} integrates closely with the Envoy project, you might also consider joining the Envoy early disclosure group. Even if not, you are still expected to abide by their embargo policy when a {{< reuse "docs/snippets/product-name.md" >}} vulnerability relates to the Envoy project.

## Updates and questions

The {{< reuse "docs/snippets/product-name.md" >}} team reserves the right to change this process. The {{< reuse "docs/snippets/product-name.md" >}} team’s security processes are reviewed regularly to ensure compliance with industry standards and the current security landscape. For questions or additional details, email the private Google group `k8s-gateway-vulnerability-reports@googlegroups.com`.
