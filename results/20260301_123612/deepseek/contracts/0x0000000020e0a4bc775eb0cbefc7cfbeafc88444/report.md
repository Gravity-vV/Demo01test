[
  {
    "Issue": "Reentrancy vulnerability in withdrawUpTo and submitClaim functions",
    "Severity": "High",
    "Description": "Both functions perform external transfers before completing state changes, violating checks-effects-interactions pattern. This appears in the smart contract code only.",
    "Impact": "Potential for fund theft through reentrant attacks.",
    "Location": "LogOfClaimedMEVBlocks.withdrawUpTo() line 56, submitClaim() line 91"
  },
  {
    "Issue": "Critical arithmetic error in miner payments",
    "Severity": "High",
    "Description": "Payment calculation divides by extremely large number (16^40), resulting in zero-value transfers. Appears in smart contract code only.",
    "Impact": "Miner payments will fail completely, receiving zero ETH.",
    "Location": "GasOptimisedPayoutsToMiners.dispersePaymentForShares() line with singlePayout / (16 ** 40)"
  },
  {
    "Issue": "Unsafe transfer() usage",
    "Severity": "Medium",
    "Description": "Using transfer() with fixed gas stipend risks failed transactions. Appears in smart contract code and static analysis results.",
    "Impact": "Funds could become stuck if transfers fail.",
    "Location": "LogOfClaimedMEVBlocks.withdrawUpTo(), submitClaim()"
  },
  {
    "Issue": "Unbounded payment loop",
    "Severity": "Medium",
    "Description": "Payment loop processes arbitrary-length array without gas limit protection. Appears in smart contract code and static analysis results.",
    "Impact": "Potential DOS through gas exhaustion.",
    "Location": "GasOptimisedPayoutsToMiners.dispersePaymentForShares()"
  },
  {
    "Issue": "Arithmetic overflow risks",
    "Severity": "Medium",
    "Description": "Multiple arithmetic operations performed without overflow checks in Solidity <0.8.0. Appears in smart contract code only.",
    "Impact": "Potential for incorrect calculations in edge cases.",
    "Location": "LogOfClaimedMEVBlocks: timestamp addition, balance adjustments"
  },
  {
    "Issue": "Zero-deposit lockup possible",
    "Severity": "Medium",
    "Description": "Can set lockup timestamps without depositing funds. Appears in smart contract code only.",
    "Impact": "Potential account locking without financial stake.",
    "Location": "LogOfClaimedMEVBlocks.depositAndLock()"
  },
  {
    "Issue": "State changes after transfer in submitClaim",
    "Severity": "Medium",
    "Description": "DepositedEther deduction occurs after transfer, violating checks-effects-interactions. Appears in smart contract code only.",
    "Impact": "Potential for inconsistent state if transfer fails.",
    "Location": "LogOfClaimedMEVBlocks.submitClaim() line 91"
  },
  {
    "Issue": "Non-standard FLAG_BLOCK_NONCE handling",
    "Severity": "Low",
    "Description": "Unusual boundary conditions in nonce flagging mechanism. Appears in smart contract code only.",
    "Impact": "Potential confusion or integration issues.",
    "Location": "LogOfClaimedMEVBlocks.FLAG_BLOCK_NONCE_LIMIT usage"
  },
  {
    "Issue": "Timestamp dependency",
    "Severity": "Low",
    "Description": "Reliance on block.timestamp for lock periods. Appears in static analysis results.",
    "Impact": "Minor manipulation possible.",
    "Location": "LogOfClaimedMEVBlocks.withdrawUpTo(), remainingDurationForWorkClaim()"
  }
]