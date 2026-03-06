[
  {
    "Issue": "Inadequate Access Control",
    "Severity": "High",
    "Description": "The contract lacks proper access control mechanisms such as ownership patterns or role-based access control. This appears in the smart contract code only.",
    "Impact": "No way to stop malicious transfers, adjust burn rate, or upgrade contract. Complete immutability post-deployment limits contract's ability to respond to issues.",
    "Location": "Contract-wide issue (no specific functions implementing access control)"
  },
  {
    "Issue": "Violation of Checks-Effects-Interactions Pattern",
    "Severity": "Medium",
    "Description": "The transfer functions violate the checks-effects-interactions pattern by performing state changes before completing all checks. This appears in the smart contract code only.",
    "Impact": "Potential reentrancy vulnerabilities if contract is modified in future. Could cause issues with token hooks or callbacks.",
    "Location": "transfer() and transferFrom() functions"
  },
  {
    "Issue": "Unprotected Division Operation",
    "Severity": "Medium",
    "Description": "The SafeMath.div function lacks protection against division by zero. This appears in the smart contract code only.",
    "Impact": "Could cause transaction reverts if called with zero denominator. Potential disruption of contract operations.",
    "Location": "SafeMath library, div() function"
  },
  {
    "Issue": "Front-running Vulnerability",
    "Severity": "Medium",
    "Description": "The deterministic burn calculation allows potential front-running of transfer transactions. This appears in the smart contract code only.",
    "Impact": "Economic inefficiency and potential griefing attacks through forced transaction ordering.",
    "Location": "transfer(), transferFrom(), and findOnePercent() functions"
  },
  {
    "Issue": "Potential Arithmetic Boundary Issues",
    "Severity": "Medium",
    "Description": "The findOnePercent function may overflow with max uint256 values. This appears in the smart contract code only.",
    "Impact": "Could prevent large transfers from executing due to overflow reverts.",
    "Location": "findOnePercent() function and its use of SafeMath.ceil()"
  }
]