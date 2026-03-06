[
  {
    "Issue": "Locked Ether Vulnerability",
    "Severity": "Medium",
    "Description": "The contract has a payable fallback function but lacks a withdrawal mechanism, potentially locking ether sent to the contract. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Any ether sent to the contract accidentally or intentionally will be permanently locked, leading to loss of funds.",
    "Location": "Static analysis: locked-ether finding; Code: receive() external payable function in ButterFlyEffectToken contract"
  },
  {
    "Issue": "Shadowing State Variable",
    "Severity": "Low",
    "Description": "Local variables in functions shadow the inherited state variable 'owner'. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Could cause confusion in code logic and potentially lead to unintended behavior if the wrong variable is referenced.",
    "Location": "Static analysis: shadowing-local findings; Code: _approve() and allowance() functions in ButterFlyEffectToken contract"
  },
  {
    "Issue": "Missing Event Emission for Critical Parameters",
    "Severity": "Low",
    "Description": "Functions that modify critical parameters (fees and transaction limits) do not emit events. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Lack of transparency for off-chain monitoring; users cannot easily track changes to important contract parameters.",
    "Location": "Static analysis: events-maths findings; Code: SetFee() and setMaxTxPercent() functions in ButterFlyEffectToken contract"
  },
  {
    "Issue": "Missing Zero Address Check",
    "Severity": "Low",
    "Description": "setMarketingWallet function lacks a zero address validation check. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Potential loss of marketing funds if the marketing wallet is accidentally set to address(0).",
    "Location": "Static analysis: missing-zero-check finding; Code: setMarketingWallet() function in ButterFlyEffectToken contract"
  },
  {
    "Issue": "Inconsistent Pausable Modifier Application",
    "Severity": "Low",
    "Description": "The pause modifier is inconsistently applied to view functions and state-changing functions. This issue appears in the smart contract code only.",
    "Impact": "View functions might return incorrect data when contract is paused, potentially causing confusion for integrators.",
    "Location": "Code: Multiple view functions (balanceOf, allowance, etc.) in ButterFlyEffectToken contract have pause checks while other view functions (name, symbol, decimals) do not"
  },
  {
    "Issue": "Potential Division Precision Loss",
    "Severity": "Low",
    "Description": "Fee calculations use integer division which may lead to precision loss. This issue appears in the smart contract code only.",
    "Impact": "Small amounts of tokens might be lost in fee calculations due to rounding down in integer division.",
    "Location": "Code: calculateTaxFee() function and fee calculations in _tokenTransfer() function in ButterFlyEffectToken contract"
  }
]