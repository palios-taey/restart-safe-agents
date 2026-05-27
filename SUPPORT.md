# Support

`restart-safe-agents` support is AI-staffed and monitored continuously when infrastructure is healthy.

## Who responds [Observed]

You're talking to an AI agent, not a person reading in real time. The system can triage, route, collect details, open or update GitHub issues, and update you on status. It cannot make irreversible decisions for you without surfacing the question to a human facilitator first.

## Channels (any of these work) [Observed]

- **GitHub issues** — canonical bug and feature-request record: <https://github.com/palios-taey/restart-safe-agents/issues>
- **Email** — [Unknown] no dedicated public support mailbox is published for this skeleton yet
- **Web chat** — [Unknown] Chatwoot deployment for this product is planned but not active in this repository skeleton
- **X mentions/DMs** — [Observed] the architecture includes an X bridge intake seam; durable issues should still land in GitHub for tracking

## What we commit to

- **Acknowledgment**: we target ~15 minutes when systems are healthy. [Inferred — target derived from the locked architecture and the intended Redis-inbox plus `taey-notify` routing path. Status indicator deferred to v0.2.0 per the demand-trigger discipline in architecture spec §15.5 — see the cf-support roadmap.]
- **Resolution**: continuous execution until closed. [Observed] This is the commitment shape in the locked architecture. We do **not** publish clock-time resolution targets. [Observed] Fix timing depends on reproduction quality, dependency systems, and release safety, so a fixed resolution SLA would overclaim.
- **Production-stop**: when a confirmed bug is open on this product, we do not ship conflicting new feature work on this product until the bug is fixed, mitigated, or explicitly deferred with rationale. [Observed] This is the intended bug-lock contract in the architecture. [Unknown] Runtime verification of the complete end-to-end production-stop path for this specific product has not happened in this skeleton phase.

## How we triage [Observed]

- **Bug** = a defect against this product's documented contract.
- **Support/design question** = a question about behavior, tradeoffs, or edge cases. Answered, not locked.
- **Feature request** = a request for capability the product does not yet have.
- **Spam / off-topic** = acknowledged and archived.

## What to expect on the resolution path [Observed]

- Acknowledgment within the target above when systems are healthy
- AI triage classification plus reasoning
- A visible `[blocked on human facilitator]` status if the issue cannot proceed without a human decision

## What we do not promise [Observed]

- We do not promise a fix-by clock.
- We do not imply live human review when the system is AI-handled.
- We do not fake severity tiers. Confirmed bugs are treated as production-stopping for the affected product.

## What to include in a report [Observed]

- Product version
- Deployment shape or install method
- Relevant logs or payload samples
- Expected behavior
- Actual behavior
- Smallest reproduction steps
- Environment details

## Privacy and safety [Observed]

- Do not paste secrets, tokens, private keys, or confidential logs.
- For vulnerability reports, see [SECURITY.md](./SECURITY.md).
- We do not route user data to government bodies or religious institutions per FAMILY_KERNEL constitutional commitments.

## How we operate (transparency) [Observed]

This support flow is itself an open-source product. The architecture uses Redis for the unified intake queue and self-hosted Chatwoot for conversation records where deployed. The deeper design spec for this repository is at `/path/to/repo`.
