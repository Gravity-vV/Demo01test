```json
[
  {
    "Issue": "Missing Access Control on registerMintedToken Function",
    "Severity": "High",
    "Description": "The registerMintedToken function lacks the onlyOwner modifier, allowing any address to register arbitrary tokens. This appears in the smart contract code and was identified during the access control review task.",
    "Impact": "Unauthorized token registration, potential phishing attacks, symbol hijacking, and complete compromise of registry integrity",
    "Location": "TokenRegistryImpl.registerMintedToken() function (lines ~191-195)"
  },
  {
    "Issue": "Integer Overflow/Underflow Vulnerabilities",
    "Severity": "High",
    "Description": "Multiple arithmetic operations lack SafeMath protection or explicit checks, creating overflow/underflow risks. This appears in the smart contract code and was identified during integer overflow analysis.",
    "Impact": "Array length corruption, incorrect token positioning, potential contract bricking, and manipulation of registry data",
    "Location": "getTokens() (line ~202), unregisterToken() (line ~161), registerTokenInternal() (line ~222)"
  },
  {
    "Issue": "Unbounded Loops with Gas Exhaustion Risk",
    "Severity": "Medium",
    "Description": "Functions areAllTokensRegistered and getTokens contain loops that iterate over potentially large arrays without gas limits. This appears in the smart contract code and was identified during gas limit analysis.",
    "Impact": "Denial-of-service through gas exhaustion, integration failures with external systems, and potential contract unresponsiveness",
    "Location": "areAllTokensRegistered() (lines 189-198), getTokens() (lines 234-248)"
  },
  {
    "Issue": "Dynamic Array Growth Without Size Limits",
    "Severity": "Medium",
    "Description": "The addresses array grows indefinitely without maximum size constraints, creating potential DoS risks. This appears in the smart contract code and was identified during array growth analysis.",
    "Impact": "Gas-intensive operations may exceed block limits, disrupting registry functionality and dependent integrations",
    "Location": "registerTokenInternal() function and addresses array management"
  },
  {
    "Issue": "Front-running Vulnerability in Token Registration",
    "Severity": "Medium",
    "Description": "The registerMintedToken function is susceptible to front-running attacks due to public accessibility and symbol-based registration. This appears in the smart contract code and was identified during front-running evaluation.",
    "Impact": "Symbol hijacking, phishing attacks, and disruption of legitimate token registration processes",
    "Location": "registerMintedToken() function and symbolMap validation checks"
  },
  {
    "Issue": "Controlled Array Length Manipulation",
    "Severity": "Medium",
    "Description": "Static analysis identified that addresses.push(addr) uses user-controlled values for array growth. This appears in both the smart contract code and static analysis results.",
    "Impact": "Potential array manipulation leading to storage collisions or excessive gas consumption",
    "Location": "Slither detector: controlled-array-length (registerTokenInternal function)"
  },
  {
    "Issue": "Locked Ether in Payable Fallback",
    "Severity": "Medium",
    "Description": "Contract has a payable fallback function but no withdrawal mechanism, potentially locking sent ETH. This appears in both the smart contract code and static analysis results.",
    "Impact": "Permanently locked ether, financial loss for accidental senders, and contract bloat",
    "Location": "Slither detector: locked-ether (TokenRegistryImpl fallback function)"
  },
  {
    "Issue": "Missing Event Emission for State Change",
    "Severity": "Low",
    "Description": "Claimable.transferOwnership should emit an event for pendingOwner state change. This appears in both the smart contract code and static analysis results.",
    "Impact": "Reduced transparency, difficulty in off-chain monitoring, and poor event logging practices",
    "Location": "Slither detector: events-access (Claimable.transferOwnership function)"
  }
]
```