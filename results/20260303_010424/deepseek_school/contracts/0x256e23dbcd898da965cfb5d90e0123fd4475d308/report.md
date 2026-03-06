```json
[
  {
    "Issue": "Reentrancy in onSushiReward function",
    "Severity": "High",
    "Description": "The onSushiReward function violates Checks-Effects-Interactions pattern by making external token transfers before updating state variables. This vulnerability appears in both the smart contract code and static analysis results.",
    "Impact": "Potential theft of rewards through cross-function reentrancy attacks, allowing attackers to manipulate reward calculations and drain funds",
    "Location": "onSushiReward function (lines ~191-213), Slither reentrancy-no-eth detection"
  },
  {
    "Issue": "Inadequate reentrancy guard protection",
    "Severity": "High",
    "Description": "The lock modifier provides insufficient protection against cross-function reentrancy, allowing state manipulation through other unprotected functions. This issue appears in the smart contract code and static analysis results.",
    "Impact": "Cross-function reentrancy attacks can exploit inconsistent state to drain funds or manipulate reward distributions",
    "Location": "lock modifier implementation, Slither cross-function reentrancy warnings"
  },
  {
    "Issue": "Unauthorized initialization function",
    "Severity": "High",
    "Description": "The init() function lacks access control and can be called by any user before proper initialization. This vulnerability appears only in the smart contract code.",
    "Impact": "Attackers can take ownership of the contract and set malicious parameters, leading to complete compromise and fund theft",
    "Location": "init() function (lines ~185-194)"
  },
  {
    "Issue": "Missing access control on updatePool function",
    "Severity": "Medium",
    "Description": "The updatePool function is public and lacks onlyMCV2 modifier, allowing unauthorized state manipulation. This issue appears only in the smart contract code.",
    "Impact": "Unauthorized users can manipulate reward accumulation state, leading to incorrect reward distributions",
    "Location": "updatePool function (line ~200)"
  },
  {
    "Issue": "Precision loss in reward calculations",
    "Severity": "Medium",
    "Description": "Integer division truncation in accToken1PerShare accumulation causes systematic precision loss over time. This issue appears only in the smart contract code.",
    "Impact": "Users receive fewer rewards than entitled, with impact growing over time as truncation errors accumulate",
    "Location": "updatePool function (sushiReward.mul(ACC_TOKEN_PRECISION) / lpSupply calculation)"
  },
  {
    "Issue": "Uninitialized local variable in onSushiReward",
    "Severity": "Medium",
    "Description": "The pending variable is declared but not initialized before use, leading to undefined behavior. This issue appears in both the smart contract code and static analysis results.",
    "Location": "onSushiReward function (pending variable declaration), Slither uninitialized-local detection"
  },
  {
    "Issue": "Missing zero-address checks",
    "Severity": "Low",
    "Description": "Multiple functions lack zero-address validation for critical parameters. This issue appears in both the smart contract code and static analysis results.",
    "Impact": "Potential loss of funds or contract functionality if zero addresses are used in critical operations",
    "Location": "reclaimTokens, transferOwnership, constructor functions; Slither missing-zero-check detection"
  },
  {
    "Issue": "Timestamp dependency in comparisons",
    "Severity": "Low",
    "Description": "Multiple functions use block.timestamp for critical comparisons and calculations. This issue appears in both the smart contract code and static analysis results.",
    "Impact": "Potential manipulation through miner influence on block timestamps",
    "Location": "onSushiReward, pendingToken, updatePool functions; Slither timestamp detection"
  }
]
```