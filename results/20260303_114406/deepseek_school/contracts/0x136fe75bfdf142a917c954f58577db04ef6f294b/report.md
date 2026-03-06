[
  {
    "Issue": "Divide Before Multiply Precision Error",
    "Severity": "Medium",
    "Description": "This issue appears in both the smart contract code and static analysis results. The getmVaultRatio function performs division before multiplication when calculating delayedCPrice and numerator, which can lead to precision loss and incorrect ratio calculations.",
    "Impact": "Incorrect collateralization ratio calculations may lead to improper liquidation thresholds or unsafe borrowing positions.",
    "Location": "Strategy.getmVaultRatio() function and static analysis divide-before-multiply finding"
  },
  {
    "Issue": "Dangerous Strict Equality Checks",
    "Severity": "Medium",
    "Description": "This issue appears in both the smart contract code and static analysis results. The _deposit() function uses strict equality checks (_token == 0 and _draw == 0) which can be dangerous in financial calculations due to potential rounding errors.",
    "Impact": "May cause functions to incorrectly skip important operations or fail to handle edge cases properly.",
    "Location": "Strategy._deposit() function and static analysis incorrect-equality finding"
  },
  {
    "Issue": "Uninitialized Local Variable",
    "Severity": "Medium",
    "Description": "This issue appears in the static analysis results only. The _losss variable in prepareReturn() is declared but never initialized before use.",
    "Impact": "Uninitialized variables can lead to unexpected behavior and potential loss calculations.",
    "Location": "Strategy.prepareReturn() function - static analysis uninitialized-local finding"
  },
  {
    "Issue": "Unused Return Values from approve() Calls",
    "Severity": "Medium",
    "Description": "This issue appears in both the smart contract code and static analysis results. Multiple approve() calls ignore return values, which can be problematic as some tokens (like USDT) return boolean values instead of reverting on failure.",
    "Impact": "Token approval failures may go undetected, leading to failed transactions or unexpected behavior.",
    "Location": "Multiple locations in _approveAll(), _approveDex() functions - static analysis unused-return findings"
  },
  {
    "Issue": "Potential Reentrancy in setRewards",
    "Severity": "Medium",
    "Description": "This issue appears in the static analysis results only. The setRewards function has a potential reentrancy vulnerability where state variables are modified after external calls.",
    "Impact": "Potential reentrancy attacks could manipulate contract state during reward address changes.",
    "Location": "BaseStrategy.setRewards() - static analysis reentrancy-no-eth finding"
  },
  {
    "Issue": "Incorrect ERC20 Interface Assumptions",
    "Severity": "Medium",
    "Description": "This issue appears in the static analysis results only. The GemLike interface assumes standard ERC20 return values, but some tokens may have non-standard implementations.",
    "Impact": "Interface incompatibility may cause function calls to fail with certain token implementations.",
    "Location": "GemLike interface - static analysis erc20-interface finding"
  },
  {
    "Issue": "Unchecked Return Values from External Calls",
    "Severity": "Medium",
    "Description": "This issue appears in both the smart contract code and static analysis results. Multiple external calls (drip(), approve()) ignore return values which could indicate failed operations.",
    "Impact": "Failed external calls may go undetected, leading to incorrect state assumptions.",
    "Location": "Strategy.adjustPosition() and various approval functions - static analysis unused-return findings"
  }
]