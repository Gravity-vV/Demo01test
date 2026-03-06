```json
[
  {
    "Issue": "Incorrect Percentage Calculation in Burn Mechanism",
    "Severity": "High",
    "Description": "The findOnePercent function incorrectly calculates 10% instead of 1% due to division by 1000 instead of 10000, and uses unnecessary ceiling operations that cause over-burning. This issue appears in the smart contract code only and was identified through manual code analysis.",
    "Impact": "Users lose 10 times more tokens than intended during transfers, causing significant financial loss and disrupting token economics with unintended deflationary pressure.",
    "Location": "findOnePercent function (lines ~78-82), transfer and transferFrom functions"
  },
  {
    "Issue": "Integer Overflow Risk in Burn Calculation",
    "Severity": "High",
    "Description": "The findOnePercent function contains a potential integer overflow when calculating roundAmount.mul(oneHundredPercent) for large values. This issue appears in the smart contract code only and relates to the SWC-101 integer overflow vulnerability pattern from the retrieved evidence.",
    "Impact": "Large transfers may revert due to overflow, blocking legitimate transactions and potentially locking funds for whale transactions.",
    "Location": "findOnePercent function (line ~81), related to SWC-101 integer overflow vulnerability"
  },
  {
    "Issue": "ERC-20 Approval Race Condition",
    "Severity": "Medium",
    "Description": "The approve function is vulnerable to front-running attacks where spenders can use old allowances before new approvals take effect. This issue appears in the smart contract code only and is a known ERC-20 standard vulnerability.",
    "Impact": "Spenders may transfer more tokens than intended when allowances are reduced, violating user intent and potentially causing unexpected token transfers.",
    "Location": "approve function (lines ~107-111)"
  },
  {
    "Issue": "Allowance-Token Transfer Semantic Mismatch",
    "Severity": "Medium",
    "Description": "transferFrom deducts the full amount from allowance but only transfers amount minus burn tokens to recipient, creating a semantic mismatch. This issue appears in the smart contract code only.",
    "Impact": "Spenders lose allowance value to the burn mechanism without recipient benefit, causing integration issues with wallets and DeFi protocols expecting standard ERC-20 behavior.",
    "Location": "transferFrom function (allowance deduction logic)"
  },
  {
    "Issue": "Zero-Value Transfer Inefficiency",
    "Severity": "Low",
    "Description": "The contract processes zero-value transfers with unnecessary state changes and event emissions. This issue appears in the smart contract code only.",
    "Impact": "Wastes gas for zero-value operations, pollutes event logs, and could enable spam transactions with minimal gas cost.",
    "Location": "transfer and transferFrom functions (lack of zero-value checks)"
  },
  {
    "Issue": "Edge Case Handling in Small Transfers",
    "Severity": "Medium",
    "Description": "The ceiling operation in findOnePercent causes excessive burning for small amounts (e.g., 1 token attempts to burn 10 tokens). This issue appears in the smart contract code only.",
    "Impact": "Small transfers may revert due to insufficient balance for burn calculation, preventing legitimate small transactions and disrupting normal token operations.",
    "Location": "findOnePercent function (ceil operation), transfer functions"
  }
]
```