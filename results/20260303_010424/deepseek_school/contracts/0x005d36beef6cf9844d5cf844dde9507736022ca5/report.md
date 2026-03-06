```json
[
  {
    "Issue": "Reentrancy Vulnerability in transferFrom Function",
    "Severity": "High",
    "Description": "The transferFrom function violates the Checks-Effects-Interactions pattern by updating the allowance mapping after emitting Transfer events, creating a reentrancy vulnerability. This issue appears in the smart contract code only and was identified through manual audit analysis.",
    "Impact": "An attacker could re-enter the contract and drain tokens from approved addresses multiple times before the allowance is properly updated, potentially resulting in significant token loss.",
    "Location": "transferFrom function in WenCoinbase contract, allowance update occurs after Transfer events"
  },
  {
    "Issue": "Integer Overflow in findOnePercent Function",
    "Severity": "High",
    "Description": "The findOnePercent function contains an integer overflow vulnerability when handling extreme values (e.g., type(uint256).max) due to multiplication before division. This issue appears in the smart contract code only and was identified through manual testing with extreme values.",
    "Impact": "Transactions involving large amounts will revert, blocking legitimate transfers and potentially disrupting contract functionality, especially for users attempting to transfer their entire balance.",
    "Location": "findOnePercent function in WenCoinbase contract, roundAmount.mul(oneHundredPercent) operation"
  },
  {
    "Issue": "ERC-20 Allowance Race Condition",
    "Severity": "Medium",
    "Description": "The approve function is susceptible to the ERC-20 allowance race condition as it allows changing allowances from non-zero values without prior reset to zero. This issue appears in the smart contract code only and follows the known ERC-20 vulnerability pattern.",
    "Impact": "A malicious spender could front-run allowance changes to spend more tokens than intended, potentially resulting in financial loss for users who grant large allowances.",
    "Location": "approve function in WenCoinbase contract, line ~95-99"
  },
  {
    "Issue": "Front-Running Vulnerability in Burn Mechanism",
    "Severity": "Medium",
    "Description": "The deterministic burn calculation in transfer and transferFrom functions creates front-running opportunities where attackers can predict and profit from supply reductions. This issue appears in the smart contract code only due to the predictable ceil-based percentage calculation.",
    "Impact": "Sophisticated users can front-run transactions to profit from predictable token burning, undermining the intended deflationary mechanism and creating unfair advantages.",
    "Location": "findOnePercent function and transfer/transferFrom functions in WenCoinbase contract"
  },
  {
    "Issue": "Incorrect Percentage Calculation in findOnePercent",
    "Severity": "Medium",
    "Description": "The findOnePercent function actually calculates 10% instead of 1% due to incorrect divisor (1000 instead of 100), and the function name is misleading. This issue appears in the smart contract code only.",
    "Impact": "The token burning mechanism burns 10x more tokens than intended based on the function name, significantly altering the intended tokenomics and deflation rate.",
    "Location": "findOnePercent function in WenCoinbase contract, div(1000) operation instead of div(100)"
  },
  {
    "Issue": "Centralization Risk from Initial Token Distribution",
    "Severity": "Medium",
    "Description": "The contract deployer receives 100% of the initial token supply, creating significant centralization risk and privileged control over token economics. This issue appears in the smart contract code only.",
    "Impact": "The contract owner can manipulate token supply dynamics, influence deflation rates through strategic transfers, and control market liquidity, undermining post-deployment immutability.",
    "Location": "Constructor and _totalSupply assignment in WenCoinbase contract"
  }
]
```