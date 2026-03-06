[
  {
    "Issue": "Locked Ether Vulnerability",
    "Severity": "Medium",
    "Description": "This issue appears in both the smart contract code and static analysis results. The contract has a payable fallback function but lacks any withdrawal mechanism, meaning ether sent to the contract becomes permanently locked.",
    "Impact": "Any ether sent to the contract address (via fallback function or forced send) cannot be recovered, resulting in permanent loss of funds.",
    "Location": "Static analysis finding: 'locked-ether' detector; Code location: fallback function (line 87-92)"
  },
  {
    "Issue": "Outdated Compiler Version",
    "Severity": "Medium",
    "Description": "This issue appears in the smart contract code only. The contract uses Solidity 0.4.15 which lacks many modern security features and contains known vulnerabilities.",
    "Impact": "Increased risk of compiler-level vulnerabilities, missing security features, and potential compatibility issues with modern tooling and infrastructure.",
    "Location": "Code preamble: pragma solidity ^0.4.15"
  },
  {
    "Issue": "Potential Gas Limit Vulnerability in Loops",
    "Severity": "Low",
    "Description": "This issue appears in the smart contract code only. Multiple functions use unbounded loops over owner arrays which could exceed gas limits if the owner count grows too large.",
    "Impact": "Transactions may fail if gas requirements exceed block gas limit, potentially making contract operations unusable with large owner sets.",
    "Location": "Functions: isConfirmed(), getConfirmationCount(), getConfirmations(), getTransactionIds(), removeOwner()"
  },
  {
    "Issue": "Missing Input Validation in External Call",
    "Severity": "Low",
    "Description": "This issue appears in the smart contract code only. The external_call function does not validate that the destination address contains code before making the call.",
    "Impact": "Transactions may succeed without actually executing any code, potentially leading to false positive execution confirmations.",
    "Location": "Function: external_call() (line 245-262)"
  }
]