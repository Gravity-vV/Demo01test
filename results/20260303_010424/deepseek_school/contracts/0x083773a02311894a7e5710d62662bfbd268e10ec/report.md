[
  {
    "Issue": "Critical Access Control Vulnerability in Init Function",
    "Severity": "High",
    "Description": "The init function lacks access control, allowing any address to initialize contract parameters including setting the owner, reward token, and reward rate. This appears in the smart contract code and was identified through manual analysis.",
    "Impact": "Complete contract takeover, potential fund theft, and disruption of reward distribution mechanism.",
    "Location": "YGGRewarder.init() function, lines 191-199"
  },
  {
    "Issue": "Reentrancy Vulnerability in onSushiReward Function",
    "Severity": "High",
    "Description": "Violation of Checks-Effects-Interactions pattern where external token transfers occur before state updates (user.unpaidRewards). This appears in both the smart contract code and static analysis results (Slither reentrancy-no-eth findings).",
    "Impact": "Potential cross-function reentrancy attacks allowing reward manipulation and fund drainage.",
    "Location": "YGGRewarder.onSushiReward() function, lines 203-206 (external calls before state updates)"
  },
  {
    "Issue": "Insufficient Reentrancy Protection",
    "Severity": "High",
    "Description": "The lock modifier provides single-function reentrancy protection but does not prevent cross-function reentrancy attacks. This appears in the smart contract code and was identified through manual analysis.",
    "Impact": "Cross-function reentrancy attacks possible despite mutex, allowing state manipulation during external calls.",
    "Location": "YGGRewarder lock modifier and onSushiReward function"
  },
  {
    "Issue": "Uninitialized Local Variable",
    "Severity": "Medium",
    "Description": "The pending variable in onSushiReward function is declared but may be used without proper initialization. This appears in the static analysis results (Slither uninitialized-local finding).",
    "Impact": "Potential incorrect reward calculations or unexpected behavior.",
    "Location": "YGGRewarder.onSushiReward() function, pending variable declaration"
  },
  {
    "Issue": "Missing Zero Address Checks",
    "Severity": "Medium",
    "Description": "Multiple functions lack zero address validation for critical parameters. This appears in the static analysis results (Slither missing-zero-check findings).",
    "Impact": "Potential loss of funds or contract functionality if zero addresses are used.",
    "Location": "Constructor (_MASTERCHEF_V2), reclaimTokens (to parameter), and transferOwnership (newOwner)"
  },
  {
    "Issue": "Arithmetic Operations Not Using Safe Math",
    "Severity": "Medium",
    "Description": "Some arithmetic operations use native operators instead of BoringMath libraries, violating the requirement. This appears in the smart contract code and was identified through manual analysis.",
    "Impact": "Potential overflow/underflow vulnerabilities in edge cases.",
    "Location": "Various locations including native subtraction in onSushiReward and division operations"
  },
  {
    "Issue": "Division by Zero Risk",
    "Severity": "Medium",
    "Description": "Potential division by zero if lpSupply becomes zero during pool updates. This appears in the smart contract code and was identified through edge case testing.",
    "Impact": "Contract reverts, disrupting reward distribution and pool updates.",
    "Location": "YGGRewarder.updatePool() function, line 250 (division by lpSupply)"
  },
  {
    "Issue": "Unsafe Token Reclaim Function",
    "Severity": "Medium",
    "Description": "The reclaimTokens function allows owner to withdraw reward tokens, which could break reward distribution. This appears in the smart contract code and was identified through manual analysis.",
    "Impact": "Potential disruption of reward distribution if owner withdraws reward tokens.",
    "Location": "YGGRewarder.reclaimTokens() function"
  }
]