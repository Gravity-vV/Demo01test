[
  {
    "Issue": "Missing Access Control in registerMintedToken Function",
    "Severity": "High",
    "Description": "The registerMintedToken function lacks the onlyOwner modifier, allowing any external address to register tokens. This appears in the smart contract code only.",
    "Impact": "Unauthorized token registration, potential registry pollution, phishing attacks, and compromised registry integrity",
    "Location": "TokenRegistryImpl.registerMintedToken() function (line ~193 in contract code)"
  },
  {
    "Issue": "Integer Overflow in getTokens Function",
    "Severity": "High",
    "Description": "The getTokens function performs arithmetic operations without overflow protection for start + count calculation. This appears in both the smart contract code and static analysis results.",
    "Impact": "Potential denial of service, incorrect data retrieval, and possible out-of-bounds array access",
    "Location": "TokenRegistryImpl.getTokens() function (line ~212) and static analysis controlled-array-length finding"
  },
  {
    "Issue": "Array Index Underflow in unregisterToken Function",
    "Severity": "Medium",
    "Description": "The unregisterToken function lacks proper bounds checking for array manipulation, potentially causing underflow. This appears in the smart contract code only.",
    "Impact": "Potential contract state corruption, denial of service, and inconsistent token registry data",
    "Location": "TokenRegistryImpl.unregisterToken() function (addresses.length - 1 and pos - 1 operations)"
  },
  {
    "Issue": "Insecure Ownership Transfer Implementation",
    "Severity": "Medium",
    "Description": "The Claimable contract's two-step ownership transfer lacks validation for pending owner capability and timeout mechanism. This appears in the smart contract code only.",
    "Impact": "Potential permanent ownership lock if transferred to inaccessible address, rendering admin functions unusable",
    "Location": "Claimable.transferOwnership() and claimOwnership() functions"
  },
  {
    "Issue": "Locked Ether Vulnerability",
    "Severity": "Medium",
    "Description": "Contract has payable fallback but no withdrawal mechanism, potentially locking ether sent accidentally. This appears in static analysis results only.",
    "Impact": "Permanent loss of any ether sent to the contract address",
    "Location": "Static analysis locked-ether finding for TokenRegistryImpl contract"
  },
  {
    "Issue": "Missing Event Emission in Ownership Transfer",
    "Severity": "Low",
    "Description": "Claimable.transferOwnership should emit an event when updating pendingOwner state. This appears in static analysis results only.",
    "Impact": "Reduced transparency and auditability of ownership transfer process",
    "Location": "Static analysis events-access finding for Claimable.transferOwnership()"
  }
]