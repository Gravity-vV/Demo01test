[
  {
    "Issue": "Locked Ether Vulnerability",
    "Severity": "Medium",
    "Description": "This issue appears in both the smart contract code and the static analysis results. The contract has a payable fallback function that reverts, meaning any Ether sent to the contract will be permanently locked with no withdrawal mechanism.",
    "Impact": "Any Ether accidentally sent to the contract address will be irrecoverable, leading to permanent loss of funds.",
    "Location": "Static analysis: locked-ether finding. Code: fallback function at line 179-181 in Mobilla contract."
  },
  {
    "Issue": "Missing Zero Address Check in Ownership Transfer",
    "Severity": "Low",
    "Description": "This issue appears in both the smart contract code and the static analysis results. The transferOwnership function does not validate that the new owner address is not zero, which could accidentally transfer ownership to an invalid address.",
    "Impact": "Potential loss of contract ownership if zero address is accidentally set as new owner, making the contract unusable.",
    "Location": "Static analysis: missing-zero-check finding. Code: transferOwnership function in Owned contract (line 72-74)."
  },
  {
    "Issue": "Outdated Compiler Version",
    "Severity": "Medium",
    "Description": "This issue appears in the smart contract code only. The contract uses Solidity 0.4.18, which is outdated and contains known vulnerabilities that have been fixed in newer versions.",
    "Impact": "Increased risk of exploitation due to known compiler vulnerabilities, including potential reentrancy and other security issues.",
    "Location": "Code: pragma solidity ^0.4.18 declaration at the top of the contract file."
  },
  {
    "Issue": "Constructor Name Mismatch",
    "Severity": "Low",
    "Description": "This issue appears in the smart contract code only. The constructor is named 'FucksToken' while the contract is named 'Mobilla', which may cause deployment issues in some environments as constructor names should match contract names in older Solidity versions.",
    "Impact": "Potential deployment failures or unintended behavior if the constructor is not properly recognized.",
    "Location": "Code: Constructor function 'FucksToken' in Mobilla contract (line 96-103)."
  },
  {
    "Issue": "Inconsistent Total Supply Value",
    "Severity": "Low",
    "Description": "This issue appears in the smart contract code only. The comment states total supply as '100000000000000000000' (100 tokens with 18 decimals) but the code sets _totalSupply to '100000000000000000000000000' (100,000,000 tokens with 18 decimals), creating a significant discrepancy.",
    "Impact": "Misleading token economics and potential confusion for users and exchanges regarding the actual token supply.",
    "Location": "Code: Comment vs actual _totalSupply assignment in constructor (line 100)."
  }
]