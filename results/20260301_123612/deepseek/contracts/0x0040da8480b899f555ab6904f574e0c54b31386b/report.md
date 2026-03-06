[
  {
    "Issue": "Unlimited Minting Capability",
    "Severity": "High",
    "Description": "The owner can mint unlimited tokens through the increaseAllowance function with no supply cap. This appears in the smart contract code and was identified in multiple audit tasks.",
    "Impact": "Owner could arbitrarily inflate the token supply, destroying token value and investor trust.",
    "Location": "increaseAllowance(uint256) function"
  },
  {
    "Issue": "Weak PRNG in Approval Function",
    "Severity": "Medium",
    "Description": "The approve function uses a timestamp-based condition (now % 10000000 == 0) which creates a weak pseudo-random number generator. This appears in both the smart contract code and static analysis results.",
    "Impact": "Could allow attackers to game approvals when timing conditions are met, potentially bypassing restrictions.",
    "Location": "approve(address,uint256) function, Slither static analysis"
  },
  {
    "Issue": "Missing Zero Address Checks",
    "Severity": "Medium",
    "Description": "Critical functions Approve() and setrouteChain() lack zero address validation. This appears in the smart contract code and was flagged in static analysis.",
    "Impact": "Owner could accidentally or maliciously set critical addresses to zero, breaking functionality.",
    "Location": "Approve(address) and setrouteChain(address) functions, Slither missing-zero-check findings"
  },
  {
    "Issue": "Single-Step Ownership Transfer",
    "Severity": "Medium",
    "Description": "Ownership transfer is single-step without confirmation, risking permanent loss if incorrect address is provided. This appears only in the smart contract code.",
    "Impact": "Could lead to irrevocable loss of contract ownership if typo occurs during transfer.",
    "Location": "transferOwnership(address) function"
  },
  {
    "Issue": "Unsafe Multiplication Operation",
    "Severity": "Medium",
    "Description": "The decreaseAllowance function performs unsafe multiplication without SafeMath or bounds checking. This appears in the smart contract code and arithmetic operation audit.",
    "Impact": "Potential integer overflow if large amount is provided, leading to incorrect rTotal calculation.",
    "Location": "decreaseAllowance(uint256) function"
  },
  {
    "Issue": "Violation of Checks-Effects-Interactions Pattern",
    "Severity": "Medium",
    "Description": "The _transfer function performs an interaction check before completing state updates. This appears only in the smart contract code.",
    "Impact": "Creates potential reentrancy vulnerability if router contract becomes malicious.",
    "Location": "_transfer(address,address,uint256) function"
  },
  {
    "Issue": "Missing Events for Critical Operations",
    "Severity": "Low",
    "Description": "Functions like decreaseAllowance modify critical parameters without emitting events. This appears in both smart contract code and static analysis.",
    "Impact": "Reduces transparency and makes it harder to track important parameter changes.",
    "Location": "decreaseAllowance(uint256) function, Slither events-maths finding"
  },
  {
    "Issue": "Dangerous Strict Equality",
    "Severity": "Low",
    "Description": "The approve function uses a dangerous strict equality check with timestamps. This appears in both smart contract code and static analysis.",
    "Impact": "Potential timing-based vulnerabilities or failed transactions due to strict condition.",
    "Location": "approve(address,uint256) function, Sliffer incorrect-equality finding"
  }
]