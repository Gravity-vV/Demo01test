[
  {
    "Issue": "Unchecked Token Transfer Return Values",
    "Severity": "High",
    "Description": "The smart contract code ignores return values from ERC20 transfer calls, which can lead to silent failures when token transfers are unsuccessful. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Failed token transfers will not be detected, potentially causing loss of funds or incorrect accounting.",
    "Location": "Crowdsale.createTokens(), Crowdsale.createTokensWithoutReffer(), Crowdsale.Crowdsale(), Crowdsale.manualWithdrawToken() in code; unchecked-transfer findings in static analysis"
  },
  {
    "Issue": "Divide Before Multiply in Referral Calculation",
    "Severity": "Medium",
    "Description": "The referral bonus calculation performs division before multiplication, which can lead to precision loss and incorrect token amounts due to integer division truncation. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Incorrect token amounts may be transferred for referral bonuses, potentially leading to unfair distribution or loss of value.",
    "Location": "Crowdsale.createTokens() function; divide-before-multiply finding in static analysis"
  },
  {
    "Issue": "Missing Ownership Transfer Event",
    "Severity": "Low",
    "Description": "The transferOwnership function changes the contract owner without emitting an event, making it difficult for off-chain systems to track ownership changes. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Lack of transparency in ownership changes, making it harder to monitor and audit contract administration.",
    "Location": "Ownable.transferOwnership() function; events-access finding in static analysis"
  },
  {
    "Issue": "Missing Referral Bonus Change Event",
    "Severity": "Low",
    "Description": "The refferBonusFunction updates the referral bonus percentage without emitting an event, making it difficult to track changes to this important parameter. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Lack of transparency in referral bonus changes, reducing auditability and user confidence.",
    "Location": "Crowdsale.refferBonusFunction() function; events-maths finding in static analysis"
  },
  {
    "Issue": "External Calls in Loop",
    "Severity": "Low",
    "Description": "The airdropTokens function contains external token transfer calls within a loop, which could potentially lead to out-of-gas errors or transaction failures for large recipient lists. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Potential transaction failures and gas inefficiency when airdropping to many addresses, possibly causing incomplete airdrops.",
    "Location": "Crowdsale.airdropTokens() function; calls-loop finding in static analysis"
  },
  {
    "Issue": "Use of Deprecated Solidity Version",
    "Severity": "Medium",
    "Description": "The contract uses Solidity 0.4.24 which is outdated and contains known vulnerabilities. This issue appears in the smart contract code only.",
    "Impact": "Exposure to known security vulnerabilities and lack of modern safety features available in newer Solidity versions.",
    "Location": "pragma solidity ^0.4.24; at the top of the contract code"
  },
  {
    "Issue": "Potential Integer Overflow/Underflow",
    "Severity": "Medium",
    "Description": "The contract uses SafeMath library for arithmetic operations, but there are potential risks with older compiler versions. This issue appears in the smart contract code context only.",
    "Impact": "Possible arithmetic vulnerabilities despite SafeMath usage due to compiler version limitations.",
    "Location": "All arithmetic operations throughout the contract code using SafeMath with Solidity 0.4.24"
  }
]