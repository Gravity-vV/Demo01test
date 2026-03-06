[
  {
    "Issue": "Reentrancy in onSushiReward function",
    "Severity": "Medium",
    "Description": "This issue appears in both the smart contract code and the static analysis results. The onSushiReward function makes external calls to transfer tokens before updating state variables, which could potentially allow reentrancy attacks despite the lock modifier.",
    "Impact": "An attacker could potentially reenter the contract during token transfer and manipulate reward calculations, leading to incorrect reward distribution or fund loss.",
    "Location": "PrimateRewarder.onSushiReward function (lines with safeTransfer calls) and static analysis reentrancy-no-eth findings"
  },
  {
    "Issue": "Uninitialized local variable in onSushiReward",
    "Severity": "Medium",
    "Description": "This issue appears in the static analysis results only. The pending variable in onSushiReward is not initialized in all code paths before use.",
    "Impact": "Could lead to unexpected behavior or calculation errors in reward distribution if the variable contains garbage values.",
    "Location": "Static analysis uninitialized-local finding for PrimateRewarder.onSushiReward"
  },
  {
    "Issue": "Missing zero address checks",
    "Severity": "Low",
    "Description": "This issue appears in both the smart contract code and static analysis results. Multiple functions lack zero address validation for critical parameters.",
    "Impact": "Potential loss of funds or tokens if functions are called with zero addresses accidentally or maliciously.",
    "Location": "reclaimTokens function (to parameter), transferOwnership function (newOwner parameter), constructor (_MASTERCHEF_V2 parameter), and static analysis missing-zero-check findings"
  },
  {
    "Issue": "Timestamp dependency in reward calculations",
    "Severity": "Low",
    "Description": "This issue appears in both the smart contract code and static analysis results. Multiple functions use block.timestamp for critical reward calculations and comparisons.",
    "Impact": "Miners could potentially manipulate block timestamps to affect reward distribution calculations, though the impact is limited in this context.",
    "Location": "pendingToken, onSushiReward, and updatePool functions; static analysis timestamp findings"
  },
  {
    "Issue": "Potential integer overflow in reward calculations",
    "Severity": "Low",
    "Description": "This issue appears in the smart contract code only. Mathematical operations in reward calculations could potentially overflow if not properly constrained, though BoringMath library provides some protection.",
    "Impact": "Could lead to incorrect reward calculations or contract reverts if values become too large.",
    "Location": "Various mathematical operations in onSushiReward, pendingToken, and updatePool functions using BoringMath operations"
  },
  {
    "Issue": "Lack of input validation in init function",
    "Severity": "Low",
    "Description": "This issue appears in the smart contract code only. The init function accepts arbitrary calldata without sufficient validation of decoded parameters.",
    "Impact": "Potential initialization with invalid parameters if called incorrectly, though the function has access control.",
    "Location": "PrimateRewarder.init function"
  }
]