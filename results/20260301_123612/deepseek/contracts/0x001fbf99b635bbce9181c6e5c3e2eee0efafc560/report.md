[
  {
    "Issue": "Reentrancy vulnerability in distribute()",
    "Severity": "Medium",
    "Description": "The distribute function sends ETH to external addresses before state changes, potentially allowing reentrancy attacks. Appears in the smart contract code only.",
    "Impact": "Could disrupt distribution process or lead to improper ETH transfers.",
    "Location": "DistributeETH.distribute() function"
  },
  {
    "Issue": "Array length mismatch vulnerability",
    "Severity": "High",
    "Description": "The distribute function doesn't verify _addrs and _bals arrays are same length, risking array overflow. Appears in the smart contract code only.",
   Impact": "Could cause failed transactions or unintended ETH transfers.",
    "Location": "DistributeETH.distribute() function"
  },
  {
    "Issue": "No balance verification before distribution",
    "Severity": "High",
    Description": "Function doesn't verify sum(_bals) <= contract balance, risking failed transfers. Appears in the smart contract code only.",
    "Impact": "Could lead to partial distribution failures or locked funds.",
    "Location": "DistributeETH.distribute() function"
  },
  {
    "Issue": "Single-step ownership transfer",
    "Severity": "High",
    "Description": "Ownable lacks two-step ownership transfer, risking permanent loss of control. Appears in the smart contract code only.",
    "Impact": "Accidental transfer to wrong address could lock contract permanently.",
    Location": "Ownable.transferOwnership() function"
  },
  {
    "Issue": "Deprecated send() and throw usage",
    "Severity": "Medium",
    "Description": "Uses deprecated send() and throw instead of transfer()/revert(). Appears in the smart contract code only.",
    Impact": "Poor error handling and gas limitations could cause failures.",
    "Location": "DistributeETH.distribute() function"
  },
  {
    "Issue": "Empty payable fallback",
    "Severity": "Medium",
    Description": "Fallback accepts ETH but lacks withdrawal mechanism, risking locked funds. Appears in the smart contract code only.",
    "Impact": "Accidentally sent ETH becomes permanently inaccessible.",
    "Location": "DistributeETH fallback function"
  },
  {
    Issue": "Missing distribution event logging",
    "Severity": "Medium",
    "Description": "No events emitted for distributions, lacking transparency. Appears in the smart contract code only.",
    Impact": "Difficult to audit or verify distribution history.",
    "Location": "DistributeETH.distribute() function"
  },
  {
    "Issue": "No ownership renouncement functionality",
    Severity": "Medium",
    "Description": "Cannot permanently renounce ownership if needed. Appears in the smart contract code only.",
    "Impact": Limitation in contract management flexibility.",
    "Location": "Ownable contract"
  }
]