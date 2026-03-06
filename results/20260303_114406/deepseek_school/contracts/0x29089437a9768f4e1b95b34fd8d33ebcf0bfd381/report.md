[
  {
    "Issue": "Locked Ether Vulnerability",
    "Severity": "Medium",
    "Description": "The contract CRMTToken has a payable constructor but lacks a withdrawal function, potentially locking any Ether sent to it. This issue is identified in the static analysis results only.",
    "Impact": "Any Ether sent to the contract during deployment or through self-destruct mechanisms will be permanently locked and inaccessible.",
    "Location": "Static analysis result: locked-ether detector for CRMTToken constructor"
  },
  {
    "Issue": "Missing Event Emission on Critical State Change",
    "Severity": "Low",
    "Description": "The changeOwner function modifies the contract owner without emitting an event, reducing transparency and off-chain monitoring capabilities. This issue is identified in the static analysis results only.",
    "Impact": "Off-chain applications and users may not detect ownership changes, leading to synchronization issues or missed alerts.",
    "Location": "Static analysis result: events-access detector for CRMTToken.changeOwner(address)"
  },
  {
    "Issue": "Missing Zero Address Check in Ownership Transfer",
    "Severity": "Low",
    "Description": "The changeOwner function does not validate that the new owner address is not zero, which could inadvertently assign ownership to an invalid address. This issue is identified in the static analysis results only.",
    "Impact": "If the zero address is passed, the contract ownership could be lost permanently, rendering owner-only functions unusable.",
    "Location": "Static analysis result: missing-zero-check detector for CRMTToken.changeOwner(address)._to"
  },
  {
    "Issue": "Use of Outdated Solidity Version",
    "Severity": "Medium",
    "Description": "The contract uses Solidity 0.4.18, which lacks many modern security features and is susceptible to known vulnerabilities. This issue is identified in the smart contract code only.",
    "Impact": "Increased risk of compiler-level vulnerabilities and absence of critical security checks available in newer versions.",
    "Location": "Smart contract code: pragma solidity ^0.4.18;"
  },
  {
    "Issue": "Potential Approval Race Condition",
    "Severity": "Low",
    "Description": "The approve function in StandardToken is susceptible to the front-running race condition described in EIP-20, though the code includes a comment warning about it. This issue is identified in the smart contract code only.",
    "Impact": "Users might inadvertently allow spenders to use both old and new allowances if transactions are reordered.",
    "Location": "Smart contract code: StandardToken.approve function and associated comment"
  }
]