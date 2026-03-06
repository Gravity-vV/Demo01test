```json
[
  {
    "Issue": "Integer Overflow/Underflow Vulnerability",
    "Severity": "High",
    "Description": "The contract lacks overflow/underflow protection in transfer and transferFrom functions. This issue appears in the smart contract code and was identified during manual audit analysis. The retrieved evidence confirms this is a known vulnerability pattern (SWC-101).",
    "Impact": "Attackers could manipulate token balances, create infinite tokens via underflow, or burn tokens via overflow, completely disrupting token economics and potentially leading to fund loss.",
    "Location": "ERC20Base.transfer() lines ~49-58, ERC20Base.transferFrom() lines ~62-72"
  },
  {
    "Issue": "ERC-20 Approve Race Condition",
    "Severity": "Medium",
    "Description": "The approve function is vulnerable to the known ERC-20 race condition where a spender can front-run allowance changes. This issue appears in the smart contract code and was confirmed by retrieved external knowledge evidence showing similar vulnerabilities in other tokens like USDT.",
    "Impact": "Malicious spenders could extract more tokens than intended by using both old and new allowance values, potentially getting up to double the intended allowance.",
    "Location": "ERC20Base.approve() lines 118-122"
  },
  {
    "Issue": "Locked Ether Vulnerability",
    "Severity": "Medium",
    "Description": "The constructor is payable but lacks a withdrawal mechanism, causing any Ether sent during deployment to be permanently locked. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Permanent loss of any Ether sent to the contract during deployment, representing direct financial loss with no recovery mechanism.",
    "Location": "Token.constructor() line ~104, Static analysis: locked-ether finding"
  },
  {
    "Issue": "Missing Zero Address Validation",
    "Severity": "Medium",
    "Description": "Transfer and transferFrom functions lack validation for address(0) as recipient, allowing unintended token burns. This issue appears only in the smart contract code analysis.",
    "Impact": "Users could accidentally send tokens to the zero address, resulting in permanent token loss and unintended supply reduction.",
    "Location": "ERC20Base.transfer() and transferFrom() functions"
  },
  {
    "Issue": "Non-Standard Return Value Handling",
    "Severity": "Medium",
    "Description": "Transfer and transferFrom functions return false on failure instead of reverting, which deviates from modern ERC-20 standards. This issue appears only in the smart contract code analysis.",
    "Impact": "Integration issues with protocols that expect reverts on transfer failures, potential compatibility problems with wallets and DeFi applications.",
    "Location": "ERC20Base.transfer() and transferFrom() functions"
  },
  {
    "Issue": "Constructor Parameter Shadowing",
    "Severity": "Low",
    "Description": "Constructor parameters shadow view function names, which could cause confusion. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Code readability and maintainability issues, potential developer confusion, but no direct security impact.",
    "Location": "Token.constructor() parameters, Static analysis: shadowing-local findings"
  }
]
```