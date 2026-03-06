[
  {
    "Issue": "Arbitrary ETH Transfer in Utils Functions",
    "Severity": "High",
    "Description": "The static analysis results show that Utils.swapETHForTokens and Utils.addLiquidity functions send ETH to arbitrary user-specified addresses without proper access controls. This issue is present in the static analysis results only.",
    "Impact": "Potential loss of contract ETH funds if malicious addresses are specified, leading to unauthorized transfers.",
    "Location": "Utils.swapETHForTokens(address,address,uint256) and Utils.addLiquidity(address,address,uint256,uint256) in static analysis results"
  },
  {
    "Issue": "Reentrancy Vulnerability in addTokensToJackpot",
    "Severity": "High",
    "Description": "The static analysis results indicate a reentrancy risk in BURN.addTokensToJackpot due to external calls before state updates. This issue is present in the static analysis results only.",
    "Impact": "Potential reentrancy attacks could manipulate contract state during token transfers, leading to fund loss or state corruption.",
    "Location": "BURN.addTokensToJackpot(uint256) in static analysis results"
  },
  {
    "Issue": "Reentrancy Vulnerability in _transferToExcluded",
    "Severity": "High",
    "Description": "The static analysis results show reentrancy risks in BURN._transferToExcluded due to external calls and state changes. This issue is present in the static analysis results only.",
    "Impact": "Reentrancy could allow attackers to manipulate fee calculations and token transfers during execution.",
    "Location": "BURN._transferToExcluded(address,address,uint256) in static analysis results"
  },
  {
    "Issue": "Use of Deprecated 'now' Keyword",
    "Severity": "Low",
    "Description": "The smart contract code uses 'now' for timestamping, which is deprecated in favor of 'block.timestamp'. This issue appears in the smart contract code only.",
    "Impact": "Code maintainability and future compatibility issues, though no immediate security risk.",
    "Location": "Multiple instances in BURN contract, e.g., round[1].startTime = now;"
  },
  {
    "Issue": "Potential Integer Overflow in SafeMath Operations",
    "Severity": "Low",
    "Description": "While SafeMath library is used, the static analysis results indicate potential arithmetic issues. This issue is inferred from code patterns and static analysis.",
    "Impact": "If not properly handled, integer overflows/underflows could lead to incorrect calculations.",
    "Location": "SafeMath functions in smart contract code and static analysis references"
  },
  {
    "Issue": "Lack of Access Control in Charity Address Change",
    "Severity": "Medium",
    "Description": "The changeCharityAddress function is onlyOwner protected, but the static analysis shows potential arbitrary send issues. This appears in both code and static analysis.",
    "Impact": "If owner is compromised, charity funds could be redirected to malicious addresses.",
    "Location": "BURN.changeCharityAddress(address) in code and static analysis"
  },
  {
    "Issue": "Insufficient Event Emission for Critical Operations",
    "Severity": "Low",
    "Description": "Key functions like charity address changes and token migrations lack event emissions for transparency. This issue is based on code patterns only.",
    "Impact": "Reduced transparency and auditability for important contract operations.",
    "Location": "BURN.changeCharityAddress and BURN.migrateToken functions in code"
  }
]