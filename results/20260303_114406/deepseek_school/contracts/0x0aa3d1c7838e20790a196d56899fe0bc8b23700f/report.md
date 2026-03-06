[
  {
    "Issue": "Cross-Function Reentrancy in exit() Function",
    "Severity": "High",
    "Description": "The exit() function contains external calls that could lead to reentrancy attacks. The static analysis results specifically identify this as a reentrancy-eth vulnerability where external calls are made before state updates, potentially allowing recursive calls.",
    "Impact": "An attacker could recursively call the exit() function to drain funds or manipulate contract state before balances are updated.",
    "Location": "PoolOwners.exit() function and static analysis reentrancy-eth finding"
  },
  {
    "Issue": "Reentrancy in Allowance Minting/Burning Functions",
    "Severity": "Medium",
    "Description": "The _mintAllowance() and _burnAllowance() functions update state variables after external calls to mint/burn allowance tokens. This pattern is vulnerable to reentrancy attacks as identified in the static analysis results.",
    "Impact": "An attacker could manipulate the minting/burning process to gain unauthorized allowance tokens or disrupt the token accounting system.",
    "Location": "PoolOwners._mintAllowance() and _burnAllowance() functions, static analysis reentrancy-no-eth findings"
  },
  {
    "Issue": "External Calls in Loop",
    "Severity": "Low",
    "Description": "The _withdrawReward() function contains external calls inside a loop, which could lead to gas limitations and potential denial-of-service if the number of reward tokens becomes too large.",
    "Impact": "Users may be unable to withdraw rewards if gas costs exceed block limits, and the contract could become unusable if too many reward tokens are added.",
    "Location": "PoolOwners._withdrawReward() function, static analysis calls-loop finding"
  },
  {
    "Issue": "Benign Reentrancy in State Update Functions",
    "Severity": "Low",
    "Description": "The withdraw() and _stake() functions update state variables after external calls, creating potential reentrancy vectors. While currently not exploitable for fund theft, this pattern could lead to unexpected behavior if the contract evolves.",
    "Impact": "Potential for state inconsistencies or unexpected behavior if external contracts interact with these functions in malicious ways.",
    "Location": "PoolOwners.withdraw() and _stake() functions, static analysis reentrancy-benign findings"
  },
  {
    "Issue": "Event Emission After External Calls",
    "Severity": "Low",
    "Description": "The exit() function emits events after making external calls, which could be manipulated by a reentrant attack to emit incorrect event data.",
    "Impact": "Inaccurate event logging could mislead external systems monitoring contract activity.",
    "Location": "PoolOwners.exit() function, static analysis reentrancy-events finding"
  }
]