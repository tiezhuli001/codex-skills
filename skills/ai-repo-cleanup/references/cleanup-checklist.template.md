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

## Audit Context
- **Audit scope for this run:**
- **Primary evidence sources used:**
- **Important missing or downgraded tools:**
- **What this audit intentionally did not prove:**

## Execution Intent
- **Execution outcome for this round:** `actionable-cleanup | zero-action-round`
- **Execution goal for the coding agent:** remove, retire, merge back, or archive the items below in priority order.
- **How to use this package:** start at `Execution Ladder` Phase 1 and keep going until every `delete-ready` and `high-probability` item is resolved or blocked by failed proof, failed verification, or evidence conflict.
- **Do not reopen broad analysis unless:** proof fails, verification fails, or runtime evidence contradicts the checklist.

## Repository Goal and Module Map
- **Repository goal / project target:**
- **Runtime / execution model:**
- **Core-path modules:**
- **Supporting modules:**
- **Edge modules:**
- **Current growth hotspots:**

## Delete-ready Now
| Item | Path(s) | Planned action | Why delete-ready | Minimum verification | Expected slimming value | Module sheet |
|---|---|---|---|---|---|---|
| `{{DELETE_READY_ITEM}}` | `...` | `delete | retire tests | merge back | archive` | `...` | `...` | `low | medium | high` | `...` |

## High-Probability Next
| Item | Path(s) | Planned action after proof | Why likely removable | Missing proof | Fastest proof to gather | Minimum verification after change | Module sheet |
|---|---|---|---|---|---|---|---|
| `{{HIGH_PROBABILITY_ITEM}}` | `...` | `...` | `...` | `...` | `...` | `...` | `...` |

## Later-phase Only
| Item | Path(s) | Why later-phase | What must happen first |
|---|---|---|---|
| `{{LATER_PHASE_ITEM}}` | `...` | `...` | `...` |

## Zero-Action Round Summary
Use this section only when both action tables are empty.
- **Current round conclusion:** no new delete-ready or high-probability cleanup slices were found.
- **Only later-phase candidate worth keeping alive:**
- **Do Not Misclassify This Round:**
  -
- **Why no module sheets were generated:** no current-round action required.

## Execution Brief
### Start Here
-

### Current Mandatory Work
-

### Do Not Waste Time On
-

### Stop Only If
- proof fails
- verification fails
- runtime evidence conflicts with the checklist

## Execution Ladder
### Phase 1 — Delete-ready now
- **Target:**
- **Primary files:**
- **Minimum verification set:**
- **Completion signal:**

### Phase 2 — High-probability after one proof
- **Target:**
- **Proof to gather first:**
- **Primary files:**
- **Minimum verification set:**
- **Completion signal:**

### Phase 3 — Later-phase only
- Keep this phase short.

## Do Not Misclassify This Round
List only the non-action items that the coding agent must consciously avoid this round.
-

## Module Coverage Map
Use only when module sheets actually exist this round.
| Module | Included this round? | Why included or excluded | Module sheet path | Execution phase role |
|---|---|---|---|---|
| `{{MODULE_NAME}}` | `yes | no` | `...` | `...` | `delete-ready | high-probability | hold-boundary | excluded` |
