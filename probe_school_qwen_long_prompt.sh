#!/bin/zsh
set -euo pipefail

ROOT="/Users/hh/MacCodes/reaserch/demo01/SmartAuditFlow/smart-contract-audit"
ENV_FILE="$ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE" >/dev/null 2>&1 || true
  set +a
fi

if [[ -z "${DEEPSEEK_SCHOOL_BASE_URL:-}" || -z "${DEEPSEEK_SCHOOL_API_KEY:-}" || -z "${DEEPSEEK_SCHOOL_MODEL_NAME:-}" ]]; then
  echo "missing school gateway env vars"
  exit 2
fi

LINES="${1:-2000}"
PROMPT_FILE="${2:-/tmp/qwen_school_long_prompt.txt}"
RESP_FILE="/tmp/qwen_school_probe_response.json"

cat > "$PROMPT_FILE" <<'EOF'
你是资深智能合约安全审计员。请对下列合约进行深入审计：
1. 列出关键风险点
2. 给出具体函数位置
3. 说明可能的利用路径
4. 给出修复建议

合约代码：
contract Vault {
    mapping(address => uint256) public balances;
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "insufficient");
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok, "transfer failed");
        balances[msg.sender] -= amount;
    }
}

请严格围绕安全问题展开，尽可能详细。
EOF

yes "请继续分析更多边界条件、攻击路径、状态转换风险、权限滥用场景和修复策略。" | head -n "$LINES" >> "$PROMPT_FILE"

PAYLOAD="$(jq -Rs --arg model "$DEEPSEEK_SCHOOL_MODEL_NAME" '
{
  model: $model,
  messages: [
    {role:"system", content:"You are a smart contract security auditor."},
    {role:"user", content:.}
  ],
  stream: false
}
' "$PROMPT_FILE")"

START_TS="$(date +%s)"
HTTP_STATUS="$(
  curl -sS "$DEEPSEEK_SCHOOL_BASE_URL/chat/completions" \
    -H "Authorization: Bearer $DEEPSEEK_SCHOOL_API_KEY" \
    -H "Content-Type: application/json" \
    --max-time 1200 \
    -o "$RESP_FILE" \
    -w "%{http_code}" \
    -d "$PAYLOAD"
)"
END_TS="$(date +%s)"
ELAPSED="$((END_TS - START_TS))"

CONTENT_SOURCE="$(
  jq -r '
    if (.choices[0].message.content | type? == "string") and ((.choices[0].message.content // "") != "") then "message.content"
    elif (.choices[0].message.content | type? == "array") then "message.content[]"
    elif ((.choices[0].text // "") != "") then "text"
    elif ((.choices[0].message.reasoning // "") != "") then "message.reasoning"
    elif ((.choices[0].message.reasoning_content // "") != "") then "message.reasoning_content"
    else "EMPTY"
    end
  ' "$RESP_FILE"
)"

CONTENT_TEXT="$(
  jq -r '
    .choices[0].message.content
    // .choices[0].text
    // .choices[0].message.reasoning
    // .choices[0].message.reasoning_content
    // ""
  ' "$RESP_FILE"
)"

FINISH_REASON="$(jq -r '.choices[0].finish_reason // "unknown"' "$RESP_FILE")"
USAGE_JSON="$(jq -c '.usage // {}' "$RESP_FILE")"
CONTENT_LEN="$(printf "%s" "$CONTENT_TEXT" | wc -c | tr -d ' ')"

echo "http_status=$HTTP_STATUS"
echo "elapsed_seconds=$ELAPSED"
echo "content_source=$CONTENT_SOURCE"
echo "finish_reason=$FINISH_REASON"
echo "content_length=$CONTENT_LEN"
echo "usage=$USAGE_JSON"
echo "preview:"
printf "%s\n" "$CONTENT_TEXT" | sed -n '1,40p'
