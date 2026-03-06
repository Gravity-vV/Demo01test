[
  {
    "Issue": "Integer Overflow/Underflow Vulnerability",
    "Severity": "High",
    "Description": "The contract contains critical integer overflow/underflow vulnerabilities in transfer and transferFrom functions due to unchecked arithmetic operations. This issue appears in the smart contract code only and was identified through manual audit analysis.",
    "Impact": "Attackers can manipulate token balances to create tokens out of thin air or drain balances from other accounts, compromising the entire token economy.",
    "Location": "ERC20Base.transfer() and ERC20Base.transferFrom() functions"
  },
  {
    "Issue": "Access Control Violation in transferFrom",
    "Severity": "High",
    "Description": "The transferFrom function violates the Checks-Effects-Interactions pattern by updating receiver balance before updating allowance, creating reentrancy and authorization risks. This issue appears in the smart contract code only.",
    "Impact": "Attackers could drain funds from addresses that granted allowances, bypassing intended authorization controls and potentially stealing all approved tokens.",
    "Location": "ERC20Base.transferFrom() function, lines ~78-89"
  },
  {
    "Issue": "Approve Race Condition Vulnerability",
    "Severity": "Medium",
    "Description": "The approve function is vulnerable to front-running attacks where spenders can use both old and new allowance amounts. This issue appears in the smart contract code and is supported by retrieved external knowledge evidence from audit reports.",
    "Impact": "Malicious spenders can drain more tokens than intended by front-running allowance changes, leading to financial loss for users who approve untrusted contracts.",
    "Location": "ERC20Base.approve() function and external audit report references (PeckShield audit reports)"
  },
  {
    "Issue": "Missing Zero-Address Validation",
    "Severity": "Medium",
    "Description": "Critical functions lack zero-address validation, allowing accidental token burning and locked allowances. This issue appears in the smart contract code only.",
    "Impact": "Tokens sent to zero address are permanently burned, and allowances set to zero address become irrecoverable, leading to financial loss and operational issues.",
    "Location": "ERC20Base.transfer(), transferFrom(), and approve() functions"
  },
  {
    "Issue": "Locked Ether Vulnerability",
    "Severity": "Medium",
    "Description": "Contract constructor is payable but lacks withdrawal function, potentially locking ether sent to the contract. This issue appears in the static analysis results only.",
    "Impact": "Ether sent to the contract constructor becomes permanently locked and unrecoverable, resulting in financial loss.",
    "Location": "Static analysis finding: 'locked-ether' in Token.constructor"
  },
  {
    "Issue": "Variable Shadowing in Constructor",
    "Severity": "Low",
    "Description": "Constructor parameters shadow existing function names, creating potential confusion and maintenance issues. This issue appears in the static analysis results only.",
    "Impact": "Reduced code readability and potential maintenance challenges, though no direct security impact.",
    "Location": "Static analysis finding: 'shadowing-local' in Token.constructor for parameters name, symbol, decimals"
  }
]