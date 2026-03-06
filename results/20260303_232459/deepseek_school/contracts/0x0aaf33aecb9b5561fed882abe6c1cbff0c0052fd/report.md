```json
[
  {
    "Issue": "Reentrancy in onSushiReward function",
    "Severity": "High",
    "Description": "Cross-function reentrancy vulnerability identified in the static analysis results and confirmed in the contract code. The onSushiReward function performs external calls (safeTransfer) before updating critical state variables (user.unpaidRewards, user.amount, user.rewardDebt), violating the checks-effects-interactions pattern.",
    "Impact": "Potential for malicious ERC20 tokens to reenter and manipulate reward calculations, leading to incorrect reward distribution or fund draining",
    "Location": "EverRewarder.onSushiReward() function, Slither reentrancy-no-eth findings"
  },
  {
    "Issue": "Missing access control on init function",
    "Severity": "High",
    "Description": "Critical access control issue identified in the contract code. The init function lacks any access control modifier and is publicly callable, allowing any address to initialize the contract and become the owner.",
    "Impact": "Complete contract takeover - attacker can set themselves as owner, control reward token, reward rate, and drain funds via reclaimTokens",
    "Location": "EverRewarder.init() function - missing access control modifier"
  },
  {
    "Issue": "Insufficient initialization guard",
    "Severity": "High",
    "Description": "Issue identified in the contract code. The init function guard only checks if rewardToken == IERC20(0), which can be bypassed by draining the reward token balance and reinitializing.",
    "Impact": "Contract can be reinitialized after legitimate initialization, allowing complete takeover and fund draining",
    "Location": "EverRewarder.init() function - insufficient require(rewardToken == IERC20(0)) check"
  },
  {
    "Issue": "Missing zero-address checks in reclaimTokens",
    "Severity": "Medium",
    "Description": "Issue identified in the static analysis results and confirmed in the contract code. The reclaimTokens function lacks zero-address validation for the 'to' parameter, potentially allowing tokens/ETH to be sent to address(0) and permanently burned.",
    "Impact": "Potential loss of funds if owner accidentally sends tokens to zero address",
    "Location": "EverRewarder.reclaimTokens() function, Slither missing-zero-check finding"
  },
  {
    "Issue": "Missing zero-address check in constructor",
    "Severity": "Low",
    "Description": "Issue identified in the static analysis results. The constructor lacks a zero-address check for the MASTERCHEF_V2 parameter, which could lead to contract deployment with invalid master chef address.",
    "Impact": "Contract may be deployed with invalid MASTERCHEF_V2 address, rendering it non-functional",
    "Location": "EverRewarder.constructor(), Slither missing-zero-check finding"
  },
  {
    "Issue": "Transaction-ordering dependency in reward rate changes",
    "Severity": "Medium",
    "Description": "Potential vulnerability identified through code analysis. The setRewardPerSecond function changes reward distribution rate without snapshots, creating transaction-ordering dependencies that can affect pending reward calculations.",
    "Impact": "Inconsistent reward distributions, potential for unfair reward allocation if rate changes are front-run",
    "Location": "EverRewarder.setRewardPerSecond() function affecting updatePool() and pendingToken() calculations"
  },
  {
    "Issue": "Potential front-running in reward distribution",
    "Severity": "Medium",
    "Description": "Potential vulnerability identified through code analysis. The reward calculation mechanism depends on current state and timing, allowing users to potentially front-run transactions to optimize their reward claims.",
    "Impact": "Uneven reward distribution, potential for users to extract more rewards than deserved through strategic timing",
    "Location": "EverRewarder.onSushiReward() reward calculation logic"
  },
  {
    "Issue": "Timestamp dependency in reward calculations",
    "Severity": "Low",
    "Description": "Issue identified in the static analysis results. Multiple functions use block.timestamp for comparisons and calculations, which can be minimally manipulated by miners.",
    "Impact": "Potential for minor reward calculation manipulation through timestamp manipulation",
    "Location": "EverRewarder.pendingToken(), updatePool(), onSushiReward() functions, Slither timestamp findings"
  }
]
```