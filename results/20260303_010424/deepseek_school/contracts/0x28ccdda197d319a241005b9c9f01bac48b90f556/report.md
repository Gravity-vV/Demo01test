[
  {
    "Issue": "Integer Overflow/Underflow Vulnerability",
    "Severity": "High",
    "Description": "Multiple arithmetic operations in transfer, transferFrom, and redeemPackage functions lack overflow/underflow protection. This appears in the smart contract code only, as static analysis failed due to compiler version mismatch.",
    "Impact": "Potential token balance manipulation, unlimited token minting, and complete contract compromise through arithmetic exploitation.",
    "Location": "transfer() function (lines ~58-67), transferFrom() function (lines ~70-84), redeemPackage() function (lines ~125-126)"
  },
  {
    "Issue": "Reentrancy Vulnerability Pattern",
    "Severity": "High",
    "Description": "State changes occur before event emissions in redeemPackage function, violating Checks-Effects-Interactions pattern. This appears in the smart contract code only.",
    "Impact": "Potential reentrancy attacks if external calls are added in future modifications, allowing multiple redemptions and token theft.",
    "Location": "redeemPackage() function (lines ~99-119) - state updates before Transfer event emission"
  },
  {
    "Issue": "Missing Access Control in redeemPackage",
    "Severity": "Critical",
    "Description": "The redeemPackage function allows anyone to redeem tokens for any recipient without authorization checks. This appears in the smart contract code only.",
    "Impact": "Complete airdrop compromise - attackers can steal all unclaimed tokens by front-running legitimate redemption transactions.",
    "Location": "redeemPackage() function (lines ~88-112) - no caller validation or recipient authorization"
  },
  {
    "Issue": "Front-Running Vulnerability",
    "Severity": "Medium",
    "Description": "Merkle proof verification occurs before redemption state marking, allowing front-running attacks. This appears in the smart contract code only.",
    "Impact": "Attackers can intercept valid redemption transactions and claim tokens intended for legitimate recipients.",
    "Location": "redeemPackage() function (lines ~89-112) - proof verification before redemption marking"
  },
  {
    "Issue": "Outdated Solidity Version",
    "Severity": "High",
    "Description": "Contract uses Solidity 0.4.17 which lacks built-in overflow protection and modern security features. This appears in both the smart contract code and static analysis results.",
    "Impact": "Increased vulnerability surface due to missing compiler-level security features and outdated language constructs.",
    "Location": "pragma solidity ^0.4.17; and throughout contract codebase"
  },
  {
    "Issue": "Missing Administrative Functions",
    "Severity": "Medium",
    "Description": "No emergency controls (pause mechanism) or administrative functions for critical operations like rootHash updates. This appears in the smart contract code only.",
    "Impact": "Inability to respond to emergencies or correct deployment errors, potentially requiring contract redeployment for issues.",
    "Location": "Contract-wide - absence of pause/update functions for critical operations"
  },
  {
    "Issue": "Incorrect CEI Pattern in Transfer Functions",
    "Severity": "Medium",
    "Description": "Transfer and transferFrom functions follow improper state change ordering that could enable reentrancy if external calls are added. This appears in the smart contract code only.",
    "Impact": "Potential reentrancy vulnerability if contract is extended with callback mechanisms or external interactions.",
    "Location": "transfer() function (lines ~58-68), transferFrom() function (lines ~70-84)"
  }
]