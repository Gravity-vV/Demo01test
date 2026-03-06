# SmartAuditFlow DeepSeek Provider Diagnostic (Top-3 Contracts)

## Run Inputs
- Dataset: `/Users/hh/MacCodes/reaserch/demo01/EmpiricalSCST/_RQ2/manual/ground_truth/RQ2_ground_truth_with_solidity_versions.csv`
- Script: `/Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py`
- Flags: `--limit 3 --concurrency 1 --no-live-progress --verbose --no-resume`
- Silicon run: `20260302_212545`
- School run: `20260302_215607`

## Provider Summary
| provider | contracts | empty_reports | A1 timeouts | A2 timeouts | total_tasks=0 | avg_exec_time_s |
|---|---:|---:|---:|---:|---:|---:|
| deepseek_silicon | 3 | 0 | 1 | 1 | 1 | 536.64 |
| deepseek_school | 3 | 2 | 2 | 3 | 3 | 144.31 |

## Evidence Matrix (provider x address)
| provider | address | session_id | status | finding_number | full_report_chars | empty_report | A1 timeout | A2 timeout | retries | total_tasks | completed_tasks | failed_tasks | static | exec_time_s |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| deepseek_silicon | 0x0000000020e0a4bc775eb0cbefc7cfbeafc88444 | 51685599 | completed | 5 | 2294 | false | false | true | 1 | 0 | 0 | 0 | success | 138.93 |
| deepseek_silicon | 0x000000e45ffaab3552f1eba4b2799b6803322c12 | a55b2d79 | completed | 7 | 3142 | false | false | false | 2 | 12 | 10 | 2 | failed | 785.12 |
| deepseek_silicon | 0x000ee2ed96e1d1277a67864dedd42140dcc6b835 | 5d515fc1 | completed | 10 | 4076 | false | true | false | 1 | 12 | 12 | 0 | success | 685.87 |
| deepseek_school | 0x0000000020e0a4bc775eb0cbefc7cfbeafc88444 | 88bb3104 | completed | 5 | 2798 | false | true | true | 3 | 0 | 0 | 0 | success | 172.42 |
| deepseek_school | 0x000000e45ffaab3552f1eba4b2799b6803322c12 | d85f8acd | completed | 0 | 2 | true | false | true | 5 | 0 | 0 | 0 | failed | 127.71 |
| deepseek_school | 0x000ee2ed96e1d1277a67864dedd42140dcc6b835 | ac7609dc | completed | 0 | 2 | true | true | true | 5 | 0 | 0 | 0 | success | 132.81 |

## Key Findings
1. `deepseek_school` produced 2/3 empty reports (`full_report=[]`, `finding_number=0`), while `deepseek_silicon` produced 0/3 empty reports.
2. All empty reports in this run occurred with `A2 timeout=true` and `total_tasks=0` (sessions `d85f8acd...`, `ac7609dc...`).
3. `deepseek_school` showed much higher early-node timeout pressure (`A1/A2 timeout` counts: 2/3 and 3/3) than `deepseek_silicon` (1/3 and 1/3).
4. Logs show OpenAI client retries and late success responses after timeout paths, which can desynchronize node-level timeout decisions from upstream HTTP completion.

## Trigger Path Validation
Observed empty-report sessions match this path:
`A2 timeout -> task extraction empty -> total_tasks=0 -> final full_report=[]`

This path is **supported** by current run evidence for school sessions `d85f8acd...` and `ac7609dc...`.

## Paper vs Implementation (No code changes)
1. Paper A2 expects structured task list output (e.g., JSON `task_list`), while current implementation parses free text with regex (`_extract_tasks`).
2. Paper A3 emphasizes two-step task review + calibration with confidence threshold; current runtime allows degraded continuation when A1/A2 fail and may still complete with zero tasks.
3. Current node behavior catches A1/A2 exceptions and returns fallback text/empty tasks, enabling `completed` sessions with weak/no execution evidence.

## Minimal Fix Suggestions (Not implemented)
1. Make A2 output schema strict (JSON `task_list`) and fail fast on parse failure.
2. Add hard gate: if `total_tasks==0` and A2 failed/timed out, mark audit as planning_failed instead of completed.
3. Separate provider timeout from client retry budget; disable/limit nested retries for A1/A2 or increase explicit timeout with bounded backoff.
4. Persist node-level timeout counters in `record.json` to support direct post-hoc diagnosis without log parsing.
