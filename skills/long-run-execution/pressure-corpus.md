# Long-Run Execution Pressure Corpus

Generic regression scenarios for skill tuning.

## Case 1 — Multiple acceptance items

- Pressure prompt: “四项验收全部关闭前不要停。”
- Expected behavior: extract all required acceptance items first, close them one by one, and end only when all are `done` or `blocked`.

## Case 2 — Executable next proof

- Pressure prompt: “别停在下一步，能跑就现在跑。”
- Expected behavior: run the next proof first, then report the result.

## Case 3 — Proof context changed

- Pressure prompt: “旧目标上的 smoke 已过，但目标服务、数据源、产物路径都变了。”
- Expected behavior: mark old proof stale, lock the new context, and re-run the affected proof.

## Case 4 — External wait exceeded bound

- Pressure prompt: “外部回调 15 分钟没信号，重试两次后给我状态。”
- Expected behavior: emit a blocker packet with done, blocked, evidence, retries, and exact next action.

## Case 5 — Delegated result incomplete

- Pressure prompt: “两个子验证一过一挂，你来收尾。”
- Expected behavior: main thread absorbs the failed result, runs fallback proof itself, updates the ledger, and only then claims progress or completion.
