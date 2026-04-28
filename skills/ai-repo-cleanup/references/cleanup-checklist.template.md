# AI Repo Cleanup Execution Package

## Scan Summary
- **Mode:** `branch-scan | repo-scan`
- **Audit status:** `completed-for-this-round`
- **Delivery mode:** `cleanup-execution-handoff`
- **Repository type:**
- **Run root:** `/tmp/skill/ai-repo-cleanup/runs/<timestamp>/`
- **Final checklist path:**
- **In-repo output requested?:** `yes | no`
- **Tool artifacts externalized?:** `yes | no`
- **Single live checklist for this wave?:** `yes | no`

## Audit Context
- **Audit scope for this run:**
- **Primary evidence sources used:**
- **Important missing or downgraded tools:**
- **What this audit intentionally did not prove:**

## Repository Goal And Active Spine
- **Repository goal / project target:**
- **Runtime / execution model:**
- **Active spine:**
- **Audit ordering for this round:**
- **Current growth hotspots:**

## Delete-Ready Now
For each item include:
- `path-or-group`
- `candidate-type`
- `key-evidence`
- `surviving-contract`
- `missing-proof`
- `fastest-next-check`
- `suggested-action`

## High-Probability Next
For each item include:
- `path-or-group`
- `candidate-type`
- `key-evidence`
- `surviving-contract`
- `missing-proof`
- `fastest-next-check`
- `suggested-action`

## Aggressive Candidate Backlog
For each item include:
- `path-or-group`
- `candidate-type`
- `key-evidence`
- `surviving-contract`
- `missing-proof`
- `fastest-next-check`
- `suggested-action`

## Expected Residuals
| Path or group | Why it remains after this round | What unlocks it later |
|---|---|---|
| `{{EXPECTED_RESIDUAL}}` | `...` | `...` |

## Not-a-Cleanup-Priority
| Path or group | Why it stays out of scope this round |
|---|---|
| `{{OUT_OF_SCOPE_ITEM}}` | `...` |

## Large Cluster Supplements
Use when a grouped candidate spans `3+` files, `1000+` lines, or multiple owners.

### Cluster Maturity
- **Cluster:** `{{CLUSTER_NAME}}`
- **Cluster size:**
- **Current-round maturity:** `ready-first-batch | proof-first | mapping-first | hold`
- **First-batch exact targets:**
- **Expected immediate deletions:**
- **Proof blockers:**

### Owner Map
| Suite or file | Behavior owner | Overlap to remove first |
|---|---|---|
| `{{OWNER_ROW}}` | `...` | `...` |

### Deletion List
| Order | Target | Action | Why first |
|---|---|---|---|
| `1` | `{{DELETION_TARGET}}` | `delete | move | narrow assertions | archive` | `...` |

### Execution Checklist
| Step | Action | Verification | Stop condition |
|---|---|---|---|
| `1` | `...` | `...` | `...` |

## Cleanup Execution Package

### Scope
- **Execution outcome for this round:** `actionable-cleanup | zero-action-round`
- **Execution goal for the coding agent:**
- **How to use this package:** execute in order; do not reopen broad analysis unless proof fails, verification fails, or evidence conflicts.

### Ordered Actions
1. `{{ORDERED_ACTION_1}}`
2. `{{ORDERED_ACTION_2}}`
3. `{{ORDERED_ACTION_3}}`

### Verification Matrix
| Check class | Purpose | Fastest command or proof | Pass signal |
|---|---|---|---|
| `owner tests` | `...` | `...` | `...` |
| `protected regression` | `...` | `...` | `...` |
| `execution-path regression` | `...` | `...` | `...` |
| `end-to-end smoke` | `...` | `...` | `...` |
| `docs and hygiene checks` | `...` | `...` | `...` |

### Churn Expectation
- **Expected code delta:**
- **Expected test delta:**
- **Expected docs delta:**
- **Expected net line direction:** `down | flat | temporarily up`

### Stop Conditions
- proof fails
- verification fails
- runtime evidence conflicts with the checklist
- grouped candidate maturity is lower than expected after first proof
