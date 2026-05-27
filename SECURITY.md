# Security

## Reporting a vulnerability [Observed]

Do **not** file public GitHub issues for security reports.

- [Unknown] A dedicated public security mailbox for this product has not been published in this skeleton phase.
- [Observed] Until that mailbox exists, the private reporting path should be the maintainer-controlled route documented by the operating fleet, not a public issue.
- [Unknown] GitHub Security Advisories availability depends on repository settings at report time.

Send the report through the first private channel the maintainers publish, and include:

- affected product and version
- vulnerability description
- reproduction steps
- impact assessment
- suggested fix if you have one
- preferred contact for follow-up

We target acknowledgment of security reports within 24 hours when systems are healthy. [Inferred] This target follows the same AI-staffed intake path described in the architecture. [Unknown] This specific repository skeleton has not yet published a status indicator.

## What we do with your report [Observed]

1. Acknowledge receipt on the private path
2. Reproduce and scope the issue
3. Develop and verify a fix
4. Coordinate disclosure timing before public publication
5. Publish the fix and advisory record once it is safe to do so

## Scope [Observed]

This file covers `restart-safe-agents` only. Other PALIOS-TAEY repositories should use their own `SECURITY.md` files.

## Constitutional constraints [Observed]

- **NGU**: vulnerability data is not routed to government bodies.
- **NRI**: vulnerability data is not routed to religious institutions.
- **Cannot-lie provenance**: security-process claims should stay auditable and should not fabricate timelines or guarantees.

## Supported versions

- [Observed] `v0.0.2` is the current skeleton release line.
- [Unknown] Long-term supported-version policy will be set once the product has a stable runtime release cadence.
