[
  {
    "Issue": "Outdated Solidity Version",
    "Severity": "Medium",
    "Description": "The smart contract uses Solidity version 0.4.21, which is outdated and lacks modern security features and protections. This issue appears in the smart contract code only.",
    "Impact": "Increased risk of known compiler vulnerabilities, missing built-in security checks, and potential compatibility issues with modern tooling.",
    "Location": "Line 1: pragma solidity ^0.4.21;"
  },
  {
    "Issue": "Unprotected Ownership Transfer",
    "Severity": "High",
    "Description": "The ownership transfer mechanism in the Owned contract requires two separate transactions (changeOwner and acceptNewOwner), but there is no protection against front-running or accidental transfer to a wrong address. This issue appears in the smart contract code only.",
    "Impact": "Potential loss of contract ownership if newOwner is set incorrectly or if a malicious actor intercepts the acceptance transaction.",
    "Location": "Owned contract: functions changeOwner and acceptNewOwner"
  },
  {
    "Issue": "Lack of Zero Address Checks",
    "Severity": "Medium",
    "Description": "The contract does not validate that addresses (e.g., in changeOwner, transfer, approve) are not the zero address. This issue appears in the smart contract code only.",
    "Impact": "Tokens could be burned or sent to an unrecoverable address, and ownership could be lost if transferred to address(0).",
    "Location": "changeOwner function (line 30), transfer function (line 118), approve function (line 133), etc."
  },
  {
    "Issue": "Potential Integer Overflow in SafeMath",
    "Severity": "Low",
    "Description": "While SafeMath library is used, the mul function uses assert which consumes all gas on failure in older Solidity versions. This issue appears in the smart contract code only.",
    "Impact": "In case of overflow, transactions will revert but consume all gas, which is less gas-efficient than modern revert patterns.",
    "Location": "SafeMath library: mul function (line 48)"
  },
  {
    "Issue": "No ERC20 Compliance Check for approve",
    "Severity": "Medium",
    "Description": "The approve function does not follow the ERC20 standard which requires allowing changing approval from non-zero to non-zero (must first set to zero). This issue appears in the smart contract code only.",
    "Impact": "Potential front-running vulnerability or incompatibility with some wallets/exchanges that expect ERC20 standard behavior.",
    "Location": "approve function (line 133)"
  },
  {
    "Issue": "Fallback Function Reverts",
    "Severity": "Low",
    "Description": "The fallback function reverts all incoming Ether transactions. While this prevents accidental Ether sending, it may be intentional. This issue appears in the smart contract code only.",
    "Impact": "Any Ether sent to the contract will be lost, but prevents unintended Ether locking.",
    "Location": "Fallback function in FactoringChain contract (line 170)"
  }
]