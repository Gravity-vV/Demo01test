[
  {
    "Issue": "Locked Ether Vulnerability",
    "Severity": "Medium",
    "Description": "The contract has a payable receive function but no withdrawal mechanism, potentially locking ether sent to the contract. This issue appears in both the static analysis results and the contract code.",
    "Impact": "Any ether sent to the contract accidentally or intentionally becomes permanently inaccessible.",
    "Location": "Static analysis: 'locked-ether' finding; Code: receive() function at contract ButterFlyEffectToken"
  },
  {
    "Issue": "Shadowed State Variable Reference",
    "Severity": "Low",
    "Description": "Local variables in functions shadow the inherited owner() function from Ownable contract. This issue appears in both the static analysis results and the contract code.",
    "Impact": "Potential confusion in code logic and unintended behavior when referring to the contract owner.",
    "Location": "Static analysis: 'shadowing-local' findings; Code: _approve() and allowance() functions parameter named 'owner'"
  },
  {
    "Issue": "Missing Event Emission for Critical State Changes",
    "Severity": "Low",
    "Description": "Functions that modify critical parameters (fees and transaction limits) do not emit events, reducing transparency. This issue appears in both the static analysis results and the contract code.",
    "Impact": "Off-chain monitoring systems cannot track important parameter changes, reducing auditability.",
    "Location": "Static analysis: 'events-maths' findings; Code: SetFee() and setMaxTxPercent() functions"
  },
  {
    "Issue": "Missing Zero Address Check",
    "Severity": "Low",
    "Description": "setMarketingWallet function lacks validation for zero address input. This issue appears in both the static analysis results and the contract code.",
    "Impact": "Potential loss of funds if marketing wallet is set to address(0) accidentally.",
    "Location": "Static analysis: 'missing-zero-check' finding; Code: setMarketingWallet() function"
  },
  {
    "Issue": "Potential Division Precision Loss",
    "Severity": "Low",
    "Description": "Fee calculations use integer division which may lead to precision loss. This issue appears in the contract code only.",
    "Impact": "Small amounts of tokens may be lost in fee calculations due to rounding errors.",
    "Location": "Code: calculateTaxFee() function and fee calculations throughout token transfers"
  },
  {
    "Issue": "Inconsistent Pausable Modifier Application",
    "Severity": "Low",
    "Description": "Some view functions unnecessarily include pausable modifiers, while the pausable functionality might not be fully implemented. This issue appears in the contract code only.",
    "Impact": "Redundant gas usage and potential confusion in contract state management.",
    "Location": "Code: Multiple view functions with whenNotPaused modifier (e.g., balanceOf(), allowance())"
  }
]