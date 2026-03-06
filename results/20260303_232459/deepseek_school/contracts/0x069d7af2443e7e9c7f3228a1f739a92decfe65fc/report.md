[
  {
    "Issue": "Reentrancy in onSushiReward due to state changes after external call",
    "Severity": "High",
    "Description": "The onSushiReward function violates Checks-Effects-Interactions pattern by updating user.unpaidRewards after external token transfers. This vulnerability appears in both the smart contract code and was detected by static analysis.",
    "Impact": "Potential reentrancy attacks allowing manipulation of reward calculations, fund loss, or state corruption if reward token is malicious",
    "Location": "onSushiReward function, lines with safeTransfer calls followed by user.unpaidRewards updates; Static analysis reentrancy-no-eth findings"
  },
  {
    "Issue": "Missing lock modifier on reclaimTokens function",
    "Severity": "High",
    "Description": "The reclaimTokens function performs external transfers without the lock modifier, creating reentrancy vulnerability. This issue appears in the smart contract code only.",
    "Impact": "Potential reentrancy attacks allowing fund theft or state manipulation if called with malicious token contracts",
    "Location": "reclaimTokens function definition missing lock modifier"
  },
  {
    "Issue": "Reentrancy risk in reclaimTokens with malicious tokens",
    "Severity": "High",
    "Description": "The reclaimTokens function is vulnerable to reentrancy when handling malicious ERC20 tokens, despite onlyOwner restriction. This issue appears in the smart contract code only.",
    "Impact": "Potential loss of all contract funds if owner is compromised or tricked into calling with malicious token",
    "Location": "reclaimTokens function with external safeTransfer calls"
  },
  {
    "Issue": "Missing onlyMCV2 modifier on pendingTokens function",
    "Severity": "Medium",
    "Description": "The pendingTokens function lacks the onlyMCV2 modifier, allowing unauthorized access to sensitive reward data. This issue appears in the smart contract code only.",
    "Impact": "Unauthorized access to pending reward information, potential data scraping for manipulation",
    "Location": "pendingTokens function definition missing onlyMCV2 modifier"
  },
  {
    "Issue": "Missing zero-address validation in constructor",
    "Severity": "Medium",
    "Description": "The constructor lacks validation for _MASTERCHEF_V2 parameter, allowing zero address assignment. This issue appears in both the smart contract code and static analysis results.",
    "Impact": "Contract bricking if zero address is passed, requiring redeployment",
    "Location": "AmunRewarder constructor; Static analysis missing-zero-check finding"
  },
  {
    "Issue": "Missing zero-address validation for to parameter in reclaimTokens",
    "Severity": "Medium",
    "Description": "The reclaimTokens function lacks zero-address validation for the to parameter, risking irreversible fund loss. This issue appears in both the smart contract code and static analysis results.",
    "Impact": "Permanent loss of funds if to address is set to zero",
    "Location": "reclaimTokens function; Static analysis missing-zero-check finding"
  },
  {
    "Issue": "Missing zero-address validation in init function parameters",
    "Severity": "Medium",
    "Description": "The init function lacks zero-address validation for owner and masterLpToken parameters. This issue appears in the smart contract code only.",
    "Impact": "Potential contract bricking or loss of administrative control if zero addresses are set",
    "Location": "init function parameter decoding section"
  },
  {
    "Issue": "Unprotected division operations in pendingToken function",
    "Severity": "Medium",
    "Description": "The pendingToken function performs division operations without BoringMath protection, risking precision loss. This issue appears in the smart contract code only.",
    "Impact": "Inaccurate reward calculations leading to unfair distribution or dust accumulation",
    "Location": "pendingToken function division operations (/ lpSupply and / ACC_TOKEN_PRECISION)"
  },
  {
    "Issue": "Precision loss in accToken1PerShare calculation",
    "Severity": "Medium",
    "Description": "Division in accToken1PerShare calculation may round down to zero for small rewards or large LP supply. This issue appears in the smart contract code only.",
    "Impact": "Loss of reward accuracy, systematic underpayment of small rewards over time",
    "Location": "updatePool and pendingToken functions, sushiReward.mul(ACC_TOKEN_PRECISION) / lpSupply"
  },
  {
    "Issue": "Miner-influenced timestamp manipulation in reward calculations",
    "Severity": "Medium",
    "Description": "Block.timestamp usage in updatePool and pendingToken allows miner manipulation within limits. This issue appears in both the smart contract code and static analysis results.",
    "Impact": "Potential reward amount manipulation within ~15 minute range, affecting fairness",
    "Location": "updatePool and pendingToken functions; Static analysis timestamp findings"
  }
]