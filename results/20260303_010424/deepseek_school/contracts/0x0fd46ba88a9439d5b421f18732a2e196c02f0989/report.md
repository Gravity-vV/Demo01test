[
  {
    "Issue": "Missing Zero Address Check in Governance Function",
    "Severity": "High",
    "Description": "The setGovernance function lacks validation to prevent setting governance to address(0), which would permanently lock administrative functions. This issue appears in both the smart contract code and was identified in static analysis results.",
    "Impact": "Permanent loss of all administrative control, inability to add/remove minters or transfer governance, requiring contract redeployment.",
    "Location": "EFI.setGovernance() function - missing require(_governance != address(0)) check"
  },
  {
    "Issue": "SafeERC20 Return Data Validation Vulnerability",
    "Severity": "High",
    "Description": "The callOptionalReturn function in SafeERC20 library lacks proper return data length validation before ABI decoding, potentially causing reverts with non-compliant tokens. This issue appears in the smart contract code only.",
    "Impact": "Contract could become unusable with certain ERC20 tokens, potentially locking funds and breaking SafeERC20 functionality for legitimate tokens.",
    "Location": "SafeERC20.callOptionalReturn() function - missing returndata.length == 32 validation"
  },
  {
    "Issue": "ERC-20 Approval Race Condition",
    "Severity": "Medium",
    "Description": "The approve function is vulnerable to the standard ERC-20 front-running race condition when reducing allowances. This issue appears in the smart contract code only.",
    "Impact": "Potential double-spending of allowances, allowing spenders to use both old and new allowance values, leading to unintended token transfers.",
    "Location": "ERC20.approve() and _approve() functions - missing safe approve pattern implementation"
  },
  {
    "Issue": "Missing Zero Address Checks in Administrative Functions",
    "Severity": "Medium",
    "Description": "Multiple administrative functions (addMinter, removeMinter, mint) lack zero address validation for address parameters. This issue appears in the smart contract code only.",
    "Impact": "Potential addition of invalid minters, minting to zero address (burning), and operational disruptions without proper validation.",
    "Location": "EFI.addMinter(), EFI.removeMinter(), EFI.mint() functions - missing zero address checks"
  },
  {
    "Issue": "Gas Inefficiency from Repeated SLOAD Operations",
    "Severity": "Low",
    "Description": "Multiple functions perform repeated storage reads of the same variables instead of caching values in memory. This issue appears in the smart contract code only.",
    "Impact": "Higher gas costs for users, reduced contract efficiency, and unnecessary transaction expenses across many operations.",
    "Location": "ERC20.transferFrom(), increaseAllowance(), decreaseAllowance() functions - repeated _msgSender() calls"
  },
  {
    "Issue": "Variable Shadowing in Constructor",
    "Severity": "Low",
    "Description": "Constructor parameters shadow function names, creating potential confusion and maintainability issues. This issue appears in both the smart contract code and static analysis results.",
    "Impact": "Reduced code readability and potential developer confusion, though no direct security impact.",
    "Location": "ERC20Detailed.constructor() - parameter names shadow function names (name, symbol, decimals)"
  }
]