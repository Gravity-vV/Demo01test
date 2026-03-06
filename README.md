# SmartAuditFlow RQ2 Test Toolkit

This folder contains a reproducible runner for auditing EmpiricalSCST RQ2 contracts with SmartAuditFlow.

## Files

- `/Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py`
- `/Users/hh/MacCodes/reaserch/demo01/test/smartauditflow_rq2/core.py`
- `/Users/hh/MacCodes/reaserch/demo01/test/smartauditflow_rq2/rule_reports.py`
- `/Users/hh/MacCodes/reaserch/demo01/test/config.example.yaml`
- Results are written to `/Users/hh/MacCodes/reaserch/demo01/test/results/<run_id>/<model>/`

## 1) Start SmartAuditFlow (frontend + backend)

Run these commands first:

```bash
cd /Users/hh/MacCodes/reaserch/demo01/SmartAuditFlow/smart-contract-audit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

Open:

- `http://127.0.0.1:5001`

Important:

- Do **not** open `index.html` with `file://`.

## 2) Quick health checks

```bash
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:5001/api/models/info
```

## 3) Runner capabilities

- Calls SmartAuditFlow API workflow:
  - `POST /api/audit/start`
  - `GET /api/audit/<session_id>/status`
  - `GET /api/audit/<session_id>/results`
- Multi-label SWC prediction per contract:
  - `pred_swc_list` can contain multiple values from `SWC-101|SWC-105|SWC-106|SWC-107|SWC-115`
  - If none match, `pred_swc_list` is empty and `is_other=1` (`SWC-OTHER` case)
- Rule-first classification from:
  - `/Users/hh/MacCodes/reaserch/demo01/EmpiricalSCST/_RQ2/RQ2_tools_vulnerabilities.json`
  - `/Users/hh/MacCodes/reaserch/demo01/EmpiricalSCST/_RQ2/vulnerability_types.csv`
- Optional LLM fallback classification
- LLM explanation pass for final chosen label set is enabled by default
  - Uses SmartAuditFlow API: `POST /api/models/call` (no local Python imports needed)
- Optional `static_tool` input directory
- Outputs:
  - `contract_level.csv`
  - `pair_level.csv`
  - `summary_metrics.csv`
  - `rule_score_per_contract.csv`
  - `reports/<address>.md` (full audit report per contract, if available)
  - `single_contract_result.json` (single mode)
  - `run_meta.json` (run root)

## 4) Single-contract test commands (do not auto-run)

### Single model

```bash
python /Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py single \
  --address 0x01d2a52708d0d8fc4d639f09a13ae87a2aec4390 \
  --models gemini \
  --concurrency 1
```

Live progress is enabled by default.
When `--concurrency 1`, each contract uses one in-place progress line (no polling-time line breaks).
Disable it with `--no-live-progress`.
Disable final-label LLM explanation with `--no-llm-explain`.

### Multiple models

```bash
python /Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py single \
  --address 0x01d2a52708d0d8fc4d639f09a13ae87a2aec4390 \
  --models gemini,deepseek
```

### All available models

```bash
python /Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py single \
  --address 0x01d2a52708d0d8fc4d639f09a13ae87a2aec4390 \
  --models all
```

## 5) Batch run commands

### Small batch smoke test

```bash
python /Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py batch \
  --models gemini \
  --limit 20 \
  --concurrency 1
```

### Multi-model batch

```bash
python /Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py batch \
  --models gemini,deepseek \
  --limit 50 \
  --concurrency 2
```

### Resume interrupted run

Resume latest run directory:

```bash
python /Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py batch \
  --models deepseek \
  --resume
```

Resume a specific run id:

```bash
python /Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py batch \
  --models deepseek \
  --resume \
  --run-id 20260221_120000
```

### Use config file

```bash
python /Users/hh/MacCodes/reaserch/demo01/test/run_smartauditflow_rq2.py batch \
  --config /Users/hh/MacCodes/reaserch/demo01/test/config.example.yaml \
  --models all
```

## 6) Optional static_tool input

If you set `--static-tool-dir`, the script looks up files by address stem in this priority order:

1. `<address>.txt`
2. `<address>.md`
3. `<address>.json`

If `--static-tool-dir` is empty, `static_tool` is sent as empty string.

## 7) Output schema

### contract_level.csv

Columns:

- `address,session_id,audit_status,model,pred_swc_list,pred_swc_count,is_other,pred_source,pred_reason,rule_scores_json,rule_matched_json,llm_fallback_json,llm_explanation_json,full_report_available,full_report_chars,full_report_path,finding_number,execution_time,gt_swc_set,error`

Meaning:

- One row per contract address (per model).
- `pred_swc_list` is the final multi-label prediction (joined by `|`).
- `is_other=1` means the final prediction list is empty.
- `pred_reason` is the merged rule/LLM rationale text.
- `gt_swc_set` is the SWC ID set that appears for this address in ground truth (joined by `|`).
- `rule_scores_json`/`rule_matched_json` keep rule scoring details for each SWC.
- `llm_fallback_json` keeps classifier fallback response; `llm_explanation_json` keeps the explanation-pass response.
- `full_report_available=1` means backend returned `full_report`.
- `full_report_path` points to saved report file under `/Users/hh/MacCodes/reaserch/demo01/test/results/<run_id>/<model>/reports/`.

### pair_level.csv

Columns:

- `address,SWC_ID,gt_label,conflict_flag,pred_swc_list,pred_label,is_other,pred_source,session_id,model,full_report_available,full_report_chars,full_report_path`

Meaning:

- One row per `(address, SWC_ID)` pair from ground truth.
- `pred_label=1` iff this `SWC_ID` is included in `pred_swc_list`, else `0`.
- This table is the direct input for TP/FP/TN/FN metric computation.

### summary_metrics.csv

Columns:

- `scope,swc,tp,fp,tn,fn,precision,recall,f1,accuracy,other_rate`

Meaning:

- Aggregated metrics derived from `pair_level.csv`.
- `scope=overall` is across all SWCs; `scope=per_swc` is per class.
- `other_rate` is the ratio of rows marked `is_other=1` under that scope.

Write timing:

- `contract_level.csv` and `rule_score_per_contract.csv` are appended per-contract during execution.
- `pair_level.csv`, `summary_metrics.csv`, and `run_meta.json` are written after each model run finishes.
- Resume mode works by loading existing `contract_level.csv` and skipping already completed addresses.
- Address-level skipping is compatible with `--concurrency > 1` (pending address list is built before dispatch).

### rule_score_per_contract.csv

Columns:

- `address,session_id,audit_status,model,pred_swc_list,pred_source,error,score_swc_101,hit_swc_101,matched_count_swc_101,score_swc_105,hit_swc_105,matched_count_swc_105,score_swc_106,hit_swc_106,matched_count_swc_106,score_swc_107,hit_swc_107,matched_count_swc_107,score_swc_115,hit_swc_115,matched_count_swc_115,rule_scores_json,rule_matched_json`

Meaning:

- One row per contract (per model) for rule-layer scoring details.
- `score_swc_xxx` is the rule score for that SWC on this contract.
- `hit_swc_xxx=1` means `score_swc_xxx >= 1.0`.
- `matched_count_swc_xxx` is the number of matched keyword/regex events for that SWC.

## 8) Evaluation behavior for SWC-OTHER

- `SWC-OTHER` means the final `pred_swc_list` is empty.
- In pair-level evaluation, empty `pred_swc_list` is treated as prediction `0` for all 5 target SWCs.

## 9) Troubleshooting

- Frontend not loading:
- Ensure server is running on `http://127.0.0.1:5001`
- Do not use `file://` for frontend
- Start failures (`start_failed`):
  - Check API keys in `/Users/hh/MacCodes/reaserch/demo01/SmartAuditFlow/smart-contract-audit/.env`
- No available models in `--models all`:
  - Verify `/api/models/info`
- LLM fallback unavailable:
  - Verify `POST /api/models/call` is available (restart SmartAuditFlow server after updating code)
  - Example:
    - `curl -s -X POST http://127.0.0.1:5001/api/models/call -H 'Content-Type: application/json' -d '{"model":"gemini","timeout":10,"prompt":"Reply with JSON: {\"ok\":true}"}'`
