---
title: "My LFX Journey with Kgateway: Documentation improvements for OIDC and JWT IdPs integrations"
toc: false
publishDate: 2026-08-31T00:00:00-00:00
author: "Michael Uzukwu"
excludeSearch: true
---

## The email that changed everything

They say when you don't succeed at first, you try again, and again, and again.

I first applied to the [LFX Mentorship Program](https://mentorship.lfx.linuxfoundation.org/) for Term 1, 2026, between February and March. I did not get through, but I did get an interview. That experience opened my eyes. It showed me exactly what I needed to work on and where I needed to grow. Instead of feeling defeated, I felt motivated. I came back stronger for Term 2.

I had already been contributing to the kgateway project before the mentorship. I built a glossary tooltip system using Hugo shortcodes, audited over thirty technical terms, worked on a Request Header Modification guide, and even presented a live demo of a custom Rust module extension at a kgateway community meeting. I had also interacted with [Art Berger](https://github.com/artberger) on Slack during some of those contributions, so I had a sense of how he worked, and I admired his approach.

When the acceptance email for Term 2 arrived, I was overjoyed because working with Art and [Nina Polshakova](https://github.com/npolshakova) was especially what I wanted. I immediately rushed to Slack to message Art, who was already like an unofficial mentor to me, even before the mentorship officially began.


## A calm start to something big

On June 16, 2026, I officially started my LFX journey. The first meeting with Art and Nina was calm and collaborative. They broke down the project scope into weekly deliverables and gave me my first task.

Art also shared something that stuck with me. He explained the reuse shortcodes in the docs repository, how snippets are stored in `assets/kgw-docs/snippets/` and reused across files. He showed me why it mattered, not just for consistency but for maintainability across different doc sets. It was the kind of behind the scenes detail that made me realize how much thought goes into documentation architecture.

What stood out most was the energy. It was collaborative, not hierarchical. They did not just tell me what to do. They explained the *why* behind the decisions. That made me feel at home immediately. They also made it clear that I could reach out anytime, and that support made all the difference.


## What we set out to build

The goal of my project was to test and document common JWT validation scenarios and demonstrate how [kgateway](https://kgateway.dev/) integrates with multiple OAuth identity providers. The expected outcome was a repeatable documentation pattern for identity providers, with practical and reproducible YAML configurations that users could apply directly.

The main focus was creating practical integration guides connecting kgateway with three identity providers: [Keycloak](https://www.keycloak.org/), [Auth0](https://auth0.com/), and [Okta](https://www.okta.com/).

You can track all of my work and activities here: [kgateway-dev/kgateway.dev#725](https://github.com/kgateway-dev/kgateway.dev/issues/725)


## Three providers, three guides, one template

![kgateway OIDC/OAuth2 Integration](/img/blog/lfx-mentorship-2026-term2-idps.png)

The three identity providers I integrated with kgateway were:

1. **Keycloak** – I restructured the [Keycloak guide](https://kgateway.dev/docs/envoy/latest/security/oauth/keycloak/setup/) into three clear sections: setup, authorization code flow, and access token validation. I also added a ConfigMap based alternative to the manual admin UI setup, making it easier for users who prefer declarative configurations.

2. **Auth0** – I followed the same template and built a complete [Auth0 guide](https://github.com/kgateway-dev/kgateway.dev/pull/959). I set up the application, configured everything step by step, and tested both the authorization code flow and access token validation in a live cluster. I also captured screenshots along the way so users could see exactly what to expect.

3. **Okta** – This was the real challenge. I was stuck for a while, locked out of the Okta Admin Console because of an MFA enrollment loop. I could not get in and I could not proceed with the guide. But I kept digging. I searched the documentation, looked at the code, and eventually figured out the solution. I switched to a Native Application to enable the Resource Owner Password grant. The [Okta guide](https://github.com/kgateway-dev/kgateway.dev/pull/969) became one of the most rewarding parts of the entire mentorship.

That moment when everything clicked and I finally got it working was the most satisfying part of the entire mentorship. It taught me that sometimes you just have to keep pushing, even when things do not make sense.


## Lessons from feedback and collaboration

One of the highlights of the journey was a feedback exchange with Art that I still remember clearly. In [PR #890](https://github.com/kgateway-dev/kgateway.dev/pull/890) for the two-backends OAuth page, Art noticed a mismatch in the example. The Cognito configuration used HTTPS, but the curl command in the verification step was using HTTP. He pointed it out, and I realized he was absolutely right. I had missed it. I fixed it, learned why it mattered, and sent the updated PR.

That moment crystallized something for me. The feedback was not personal. It was about the work. And that made all the difference. I started looking forward to Art's comments because I knew they would help me grow.

Another memorable moment was working with Art and Nina to reorganize the Keycloak and Auth0 guides. Originally, all the content lived on a single page. During one of our meetings, we discussed splitting it into a three-page structure: setup, authorization code flow, and access token validation. Art had opened a PR that built on my work, restructuring the entire OAuth section. We collaborated on finding the right balance, whether to keep everything on one page or separate them. I argued that splitting them would improve user experience because different users come with different needs. Some just want to set up the provider. Others want browser-based login. Others want API token validation.

The result was a cleaner, more modular structure. It became a template we could reuse for Auth0 and later for Okta. That kind of collaboration, where my input shaped the final output, was deeply rewarding.


## What I will carry with me forever

This mentorship has been one of the most valuable experiences of my life. A few things stood out to me:

- **Persistence matters**, even when you are stuck. I was stuck on Okta for a while, but I did not give up and that persistence paid off.

- **Testing is everything.** Writing docs is one thing, but testing them in a real cluster is what makes them actually useful.

- **Feedback is a gift.** Art and Nina gave honest and constructive feedback. Sometimes it was tough, but it made the guides better and it made me better.

- **Open source is about people.** Beyond the code, I found a community of people who were willing to help, guide, and encourage me.


## The road ahead

I plan to continue contributing to kgateway after the mentorship ends. I would like to add guides for Entra ID and Google and stay involved in the project. The mentorship may be ending, but my journey with kgateway is just getting started.

If you are thinking of applying to the [LFX program](https://mentorship.lfx.linuxfoundation.org/), I would say go for it. It is not easy and the work is real. But if you are willing to put in the effort, communicate with your mentors, and stay curious, you will get so much out of it.


A huge thank you to [@Art](https://github.com/artberger) and [@Nina](https://github.com/npolshakova) for being awesome mentors, for the support and the fast feedback throughout the whole term.

**Cheers!**

**GitHub:** [@Mike-4-prog](https://github.com/Mike-4-prog) · **LinkedIn:** [Michael Uzukwu](https://www.linkedin.com/in/michael-uzukwu/)