The `kgateway-oss-kubernetes` skill guides a coding assistant through kgateway API gateway tasks on Kubernetes. It directs the assistant to read current kgateway and Gateway API documentation, check the release installed in your cluster, and verify traffic after a change. It can help with installation, listeners, routes, policies, and troubleshooting.

Installing the skill does not install kgateway, grant cluster access, or change any resources.

## Install the skill

From the project where you use your assistant, run:

```sh
npx skills add https://github.com/solo-io/doc-examples --skill kgateway-oss-kubernetes --agent codex
```

For Claude Code, replace `codex` with `claude-code`. The [public source folder](https://github.com/solo-io/doc-examples/tree/main/skills/kgateway-oss-kubernetes) contains the complete instructions and references. You can review it before installation or copy it into your assistant's project skill directory.

## Ask for a specific outcome

Name the Kubernetes context, the application, and the traffic behavior you want. For example:

```text
Use kgateway-oss-kubernetes in context staging to expose the catalog
service over HTTPS at catalog.example.com. Show the Helm and Gateway API
changes, verify a request through the listener, and provide rollback steps.
```

```text
Use kgateway-oss-kubernetes to add authentication to the payments route
using my existing external auth service. Check policy attachment, test an
allowed and a denied request, and preserve the current Gateway owner.
```

The assistant needs access to your project files and the selected cluster to deploy and verify a change. For a plan or review, ask for that scope. It reports which checks ran and which still need cluster access, credentials, or a reachable endpoint. For LLM, MCP, or agent traffic, use the [agentgateway documentation](https://agentgateway.dev/docs/) and its matching skill.

## Update the skill

Installed instructions do not update automatically. From the same project, run `npx skills update kgateway-oss-kubernetes --project`, then start a new assistant session. Review source changes first if your team has customized its copy.
