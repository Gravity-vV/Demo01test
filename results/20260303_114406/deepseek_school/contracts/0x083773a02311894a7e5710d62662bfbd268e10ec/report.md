[
  {
    "Issue": "Reentrancy in onSushiReward function",
    "Severity": "Medium",
    "Description": "This issue appears in both the smart contract code and static analysis results. The onSushiReward function makes external calls before updating state variables, creating a reentrancy vulnerability. The static analysis specifically identifies two instances where safeTransfer calls are made before updating user.unpaidRewards.",
    "Impact": "An attacker could potentially reenter the contract and manipulate reward calculations, leading to incorrect reward distribution or fund loss.",
    "Location": "YGGRewarder.onSushiReward function (lines with rewardToken.safeTransfer calls) and static analysis reentrancy-no-eth findings"
  },
  {
    "Issue": "Uninitialized local variable in onSushiReward",
    "Severity": "Medium",
    "Description": "This issue appears in the static analysis results only. The pending variable in onSushiReward is declared but not initialized before use, which could lead to unexpected behavior.",
    "Impact": "Uninitialized variables may contain arbitrary values, potentially leading to incorrect reward calculations or unexpected contract behavior.",
    "Location": "Static analysis uninitialized-local finding for YGGRewarder.onSushiReward"
  },
  {
    "Issue": "Missing zero address checks",
    "Severity": "Low",
    "Description": "This issue appears in both the smart contract code and static analysis results. Multiple functions lack zero address validation for critical parameters including the constructor _MASTERCHEF_V2 parameter, transferOwnership newOwner parameter, and reclaimTokens to parameter.",
    "Impact": "Transactions could be sent to address(0), resulting in permanent loss of funds or ownership assignments to invalid addresses.",
    "Location": "YGGRewarder constructor, BoringOwnable.transferOwnership, YGGRewarder.reclaimTokens functions, and static analysis missing-zero-check findings"
  },
  {
    "Issue": "Timestamp dependency in reward calculations",
    "Severity": "Low",
    "Description": "This issue appears in both the smart contract code and static analysis results. Multiple functions use block.timestamp for critical reward calculations and comparisons, which can be manipulated by miners within a limited range.",
    "Impact": "Miners could potentially manipulate timestamps to influence reward distribution timing and amounts, though the impact is limited to a small time window.",
    "Location": "YGGRewarder.updatePool, YGGRewarder.pendingToken, YGGRewarder.onSushiReward functions, and static analysis timestamp findings"
  },
  {
    "Issue": "Reentrancy event emission ordering",
    "Severity": "Low",
    "Description": "This issue appears in the static analysis results only. Events are emitted after external calls in the onSushiReward function, which could be problematic in reentrancy scenarios.",
    "Impact": "In reentrancy attacks, event logs may not accurately reflect the actual state changes, complicating debugging and monitoring.",
    "Location": "Static analysis reentrancy-events finding for YGGRewarder.onSushiReward"
  }
]