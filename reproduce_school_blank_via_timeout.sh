#!/usr/bin/env bash
set -euo pipefail

# Reproduce SmartAuditFlow-like blank output by:
# 1) forcing timeout on A1/A2 direct school-API calls,
# 2) simulating empty task extraction,
# 3) requesting final formatter and checking whether output is [].

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${ROOT:-$SCRIPT_DIR/../SmartAuditFlow/smart-contract-audit}"
if [[ ! -d "$ROOT" ]]; then
  echo "ERROR: smart-contract-audit not found at: $ROOT"
  exit 1
fi
cd "$ROOT"

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required"
  exit 1
fi

set -a
source .env >/dev/null 2>&1 || true
set +a

: "${DEEPSEEK_SCHOOL_BASE_URL:?missing DEEPSEEK_SCHOOL_BASE_URL}"
: "${DEEPSEEK_SCHOOL_API_KEY:?missing DEEPSEEK_SCHOOL_API_KEY}"
: "${DEEPSEEK_SCHOOL_MODEL_NAME:?missing DEEPSEEK_SCHOOL_MODEL_NAME}"

FORCE_TIMEOUT="${FORCE_TIMEOUT:-1}"   # 1 => force timeout for A1/A2
A1_MAX_TIME="${A1_MAX_TIME:-1}"       # only used when FORCE_TIMEOUT=1
A2_MAX_TIME="${A2_MAX_TIME:-1}"       # only used when FORCE_TIMEOUT=1
NORMAL_MAX_TIME="${NORMAL_MAX_TIME:-60}"
FINAL_MAX_TIME="${FINAL_MAX_TIME:-60}"

OUT_DIR="${OUT_DIR:-/tmp/school_blank_repro_$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$OUT_DIR"

RESP_HTTP=""
RESP_TTFB=""
RESP_TOTAL=""
RESP_CONTENT=""
RESP_BODY=""
RESP_TIMEOUT="0"

call_chat() {
  local prompt="$1"
  local max_time="$2"
  local stage="$3"

  local payload raw metrics
  payload="$(
    jq -n \
      --arg model "$DEEPSEEK_SCHOOL_MODEL_NAME" \
      --arg p "$prompt" \
      '{
        model: $model,
        messages: [
          {role:"system", content:"You are a smart contract security auditor."},
          {role:"user", content:$p}
        ],
        stream: false
      }'
  )"

  raw="$(
    curl -sS -X POST "$DEEPSEEK_SCHOOL_BASE_URL/chat/completions" \
      -H "Authorization: Bearer $DEEPSEEK_SCHOOL_API_KEY" \
      -H "Content-Type: application/json" \
      --max-time "$max_time" \
      -d "$payload" \
      -w $'\n__METRIC__ HTTP=%{http_code} TTFB=%{time_starttransfer} TOTAL=%{time_total}\n' \
      || true
  )"

  RESP_BODY="$(printf '%s\n' "$raw" | sed '$d')"
  metrics="$(printf '%s\n' "$raw" | tail -n1)"
  RESP_HTTP="$(printf '%s\n' "$metrics" | sed -n 's/.*HTTP=\([0-9]\+\).*/\1/p')"
  RESP_TTFB="$(printf '%s\n' "$metrics" | sed -n 's/.*TTFB=\([0-9.]\+\).*/\1/p')"
  RESP_TOTAL="$(printf '%s\n' "$metrics" | sed -n 's/.*TOTAL=\([0-9.]\+\).*/\1/p')"
  RESP_CONTENT="$(printf '%s\n' "$RESP_BODY" | jq -r '.choices[0].message.content // empty' 2>/dev/null || true)"

  RESP_TIMEOUT="0"
  if [[ "${RESP_HTTP:-000}" == "000" ]]; then
    RESP_TIMEOUT="1"
  fi

  printf '%s\n' "$RESP_BODY" >"$OUT_DIR/${stage}_raw.json"
  {
    echo "STAGE=$stage"
    echo "HTTP=${RESP_HTTP:-000}"
    echo "TTFB=${RESP_TTFB:-0}"
    echo "TOTAL=${RESP_TOTAL:-0}"
    echo "TIMEOUT=$RESP_TIMEOUT"
    echo "MAX_TIME=$max_time"
  } >"$OUT_DIR/${stage}_metric.txt"
}

read -r -d '' CONTRACT_CODE <<'EOF' || true
contract Vault {
  mapping(address=>uint) b;
  function dep() external payable { b[msg.sender] += msg.value; }
  function wd(uint x) external {
    require(b[msg.sender] >= x);
    (bool ok,) = msg.sender.call{value:x}("");
    require(ok);
    b[msg.sender] -= x;
  }
}
EOF

read -r -d '' A1_PROMPT <<EOF || true
Perform an initial smart contract security analysis with clear sections:
1) contract purpose
2) key state variables and fund flows
3) critical risk areas
4) suspicious patterns.

Code:
$CONTRACT_CODE
EOF

if [[ "$FORCE_TIMEOUT" == "1" ]]; then
  call_chat "$A1_PROMPT" "$A1_MAX_TIME" "a1"
else
  call_chat "$A1_PROMPT" "$NORMAL_MAX_TIME" "a1"
fi

A1_ANALYSIS="$RESP_CONTENT"
if [[ "$RESP_TIMEOUT" == "1" || "${RESP_HTTP:-000}" != "200" || -z "$A1_ANALYSIS" ]]; then
  A1_ANALYSIS="Initial analysis failed: timeout"
fi

read -r -d '' A2_PROMPT <<EOF || true
Based on the initial analysis below, create a numbered, executable audit plan.

Initial Analysis:
$A1_ANALYSIS

Code:
$CONTRACT_CODE
EOF

if [[ "$FORCE_TIMEOUT" == "1" ]]; then
  call_chat "$A2_PROMPT" "$A2_MAX_TIME" "a2"
else
  call_chat "$A2_PROMPT" "$NORMAL_MAX_TIME" "a2"
fi

A2_PLAN="$RESP_CONTENT"
TASKS_JSON="[]"
if [[ "$RESP_TIMEOUT" != "1" && "${RESP_HTTP:-000}" == "200" ]]; then
  # Keep this intentionally simple to mimic SAF failure path:
  # if parsing is not robust, we still end with empty task list.
  TASKS_JSON="[]"
fi

read -r -d '' FINAL_PROMPT <<EOF || true
You are a formatter node in a smart contract audit workflow.

Given:
- initial_analysis: $A1_ANALYSIS
- audit_plan: $A2_PLAN
- extracted_tasks: $TASKS_JSON
- task_results: []

Return ONLY a JSON array of findings.
If no reliable findings are available, return [] exactly.
EOF

call_chat "$FINAL_PROMPT" "$FINAL_MAX_TIME" "final"

FINAL_TEXT="$RESP_CONTENT"
FINAL_TRIMMED="$(printf '%s' "$FINAL_TEXT" | tr -d ' \t\r\n')"

echo "========== SUMMARY =========="
echo "A1 metric: $(cat "$OUT_DIR/a1_metric.txt" | tr '\n' ' ' )"
echo
echo "A2 metric: $(cat "$OUT_DIR/a2_metric.txt" | tr '\n' ' ' )"
echo
echo "FINAL metric: $(cat "$OUT_DIR/final_metric.txt" | tr '\n' ' ' )"
echo
echo "FINAL content:"
printf '%s\n' "$FINAL_TEXT"
echo
if [[ "$FINAL_TRIMMED" == "[]" ]]; then
  echo "REPRODUCED_EMPTY_OUTPUT=YES"
else
  echo "REPRODUCED_EMPTY_OUTPUT=NO"
fi
echo "ARTIFACT_DIR=$OUT_DIR"
