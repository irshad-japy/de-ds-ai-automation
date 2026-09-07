---
title: POC Security and Secret Handling
source: security_policy.md
category: security
effective_date: 2026-06-01
---
# POC Security and Secret Handling

API keys used during local learning must be stored in a local `.env` file that is excluded from Git. Keys must never be hard-coded in Python files or committed to GitHub. After the basic POC works, Microsoft Entra ID and managed identity should be preferred where supported. Production deployments should use least-privilege role assignments and private networking where required by the threat model.
