[
  {
    "Issue": "Reentrancy vulnerability in transferFrom function",
    "Severity": "High",
    "Description": "The transferFrom function updates state after potential external interactions (event emissions), violating checks-effects-interactions pattern. This appears in the smart contract code only and was identified during manual audit.",
    "Impact": "Potential for attackers to drain funds through recursive calls before allowances are properly updated",
    "Location": "transferFrom function, lines 118-135 in WenCoinbase contract"
  },
  {
    "Issue": "Integer underflow in SafeMath.ceil function",
    "Severity": "High",
    "Description": "The ceil function can underflow when subtracting 1 from an overflowed value. This appears in the smart contract code only and was identified during manual audit.",
    "Impact": "Denial of service for large token transfers, breaking core contract functionality",
    "Location": "SafeMath.ceil function, line 49-52 in SafeMath library"
  },
  {
    "Issue": "Missing division-by-zero check in SafeMath.div",
    "Severity": "Medium",
    "Description": "The div function lacks a zero-division check, which could cause runtime reverts. This appears in the smart contract code only and was identified during manual audit.",
    "Impact": "Transaction failures and potential denial of service if division by zero occurs",
    "Location": "SafeMath.div function, line 33-36 in SafeMath library"
  },
  {
    "Issue": "Lack of access controls for administrative functions",
    "Severity": "High",
    "Description": "No ownership controls or administrative restrictions exist, making the contract inflexible and unable to respond to emergencies. This appears in the smart contract code only and was identified during manual audit.",
    "Impact": "Cannot modify burn rate, pause transfers, or recover tokens; permanent rigid tokenomics",
    "Location": "Contract structure - missing ownership pattern throughout WenCoinbase contract"
  },
  {
    "Issue": "Front-running vulnerability in approve function",
    "Severity": "Medium",
    "Description": "Standard ERC-20 approve front-running vulnerability where spenders can use old allowances before updates. This appears in the smart contract code only and is a known ERC-20 issue.",
    "Impact": "Spenders can exceed intended allowance limits by front-running allowance reduction transactions",
    "Location": "approve function in WenCoinbase contract"
  },
  {
    "Issue": "Precision loss and calculation issues in findOnePercent",
    "Severity": "Medium",
    "Description": "The fee calculation may suffer from precision loss and uses confusing variable naming. This appears in the smart contract code only and was identified during manual audit.",
    "Impact": "Incorrect token burning amounts, affecting token economics and supply",
    "Location": "findOnePercent function in WenCoinbase contract"
  }
]