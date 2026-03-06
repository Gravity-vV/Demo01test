[
  {
    "Issue": "Reentrancy in onSushiReward function",
    "Severity": "Medium",
    "Description": "This issue appears in both the smart contract code and static analysis results. The onSushiReward function makes external token transfers before updating state variables, which could enable reentrancy attacks if the reward token is a malicious contract.",
    "Impact": "An attacker could potentially reenter the contract and manipulate reward calculations, leading to incorrect reward distribution or fund loss.",
    "Location": "PrimateRewarder.onSushiReward function (lines with safeTransfer calls) and static analysis finding: reentrancy-no-eth"
  },
  {
    "Issue": "Uninitialized local variable in onSushiReward",
    "Severity": "Medium",
    "Description": "This issue appears in the static analysis results only. The pending variable in onSushiReward is declared but not explicitly initialized before use, which could lead to unexpected behavior.",
    "Impact": "The contract may use uninitialized memory values, potentially causing incorrect reward calculations or other unexpected behavior.",
    "Location": "Static analysis finding: uninitialized-local for PrimateRewarder.onSushiReward"
  },
  {
    "Issue": "Missing zero address checks in constructor and reclaimTokens",
    "Severity": "Low",
    "Description": "This issue appears in both the smart contract code and static analysis results. The constructor and reclaimTokens function lack zero address validation for critical parameters.",
    "Impact": "Potential loss of funds if tokens are transferred to address(0) or if the MASTERCHEF_V2 address is incorrectly set to zero.",
    "Location": "PrimateRewarder constructor (MASTERCHEF_V2 assignment) and reclaimTokens function (to parameter); static analysis findings: missing-zero-check"
  },
  {
    "Issue": "Timestamp dependency in reward calculations",
    "Severity": "Low",
    "Description": "This issue appears in both the smart contract code and static analysis results. Multiple functions use block.timestamp for critical reward calculations and comparisons.",
    "Impact": "Miners can potentially manipulate block timestamps to influence reward distribution, though the impact is limited to reward timing rather than fund loss.",
    "Location": "onSushiReward, pendingToken, and updatePool functions; static analysis findings: timestamp"
  },
  {
    "Issue": "Missing access control in init function",
    "Severity": "Medium",
    "Description": "This issue appears in the smart contract code only. The init function is publicly callable and lacks access control, allowing anyone to initialize the contract parameters.",
    "Impact": "Malicious actors could initialize or reinitialize the contract with malicious parameters, potentially hijacking the reward mechanism.",
    "Location": "PrimateRewarder.init function (public visibility without access control)"
  },
  {
    "Issue": "Potential integer overflow in reward calculations",
    "Severity": "Low",
    "Description": "This issue appears in the smart contract code only. Mathematical operations in reward calculations (mul, add) use custom safe math libraries, but the precision handling and large multipliers could still potentially lead to overflow in extreme cases.",
    "Impact": "Incorrect reward calculations if extremely large values are used, potentially disrupting reward distribution.",
    "Location": "Various mathematical operations in onSushiReward, pendingToken, and updatePool functions using BoringMath libraries"
  }
]