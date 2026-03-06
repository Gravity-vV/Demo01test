[
  {
    "Issue": "Arbitrary Self-Destruct",
    "Severity": "High",
    "Description": "The setup function allows authorized users to destroy the contract and send remaining ETH to an arbitrary address. This appears in both the smart contract code and static analysis results.",
    "Impact": "Complete loss of contract functionality and potential fund theft if attacker gains authorized access.",
    "Location": "FinancialStrategy.setup() function with _state == 0, and static analysis suicidal finding"
  },
  {
    "Issue": "Uninitialized State Variables",
    "Severity": "High",
    "Description": "Critical arrays (wallets, percent, cap) are declared but never initialized, leading to potential out-of-bounds access. This appears in both the smart contract code and static analysis results.",
    "Impact": "Contract functions may revert unexpectedly or allow unauthorized access when accessing uninitialized arrays.",
    "Location": "Arrays declared at lines with uint256[0] and address[0], and static analysis uninitialized-state findings"
  },
  {
    "Issue": "Arbitrary ETH Transfer",
    "Severity": "High",
    "Description": "Multiple functions transfer ETH to arbitrary addresses without proper validation. This appears in both the smart contract code and static analysis results.",
    "Impact": "Potential fund loss if malicious addresses are specified or authorization is bypassed.",
    "Location": "refund(), getBeneficiaryCash(), getPartnerCash() functions, and static analysis arbitrary-send-eth findings"
  },
  {
    "Issue": "Dangerous Strict Equality Checks",
    "Severity": "Medium",
    "Description": "Multiple functions use strict equality checks for balance comparisons and condition checks. This appears in both the smart contract code and static analysis results.",
    "Impact": "Unexpected behavior due to rounding errors or precision issues, potentially blocking contract operations.",
    "Location": "setup() function (address(this).balance == 0), internalCalc() (free == 0), getBeneficiaryCash() (move == 0), and static analysis incorrect-equality findings"
  },
  {
    "Issue": "Missing Zero Address Validation",
    "Severity": "Low",
    "Description": "Functions transferring ETH do not validate that recipient addresses are not zero addresses. This appears in both the smart contract code and static analysis results.",
    "Impact": "Potential permanent loss of funds if ETH is sent to address(0).",
    "Location": "refund() function _investor parameter, and static analysis missing-zero-check finding"
  },
  {
    "Issue": "Benign Reentrancy Patterns",
    "Severity": "Low",
    "Description": "Multiple functions exhibit reentrancy patterns with external calls followed by state changes. This appears in both the smart contract code and static analysis results.",
    "Impact": "While not immediately exploitable, these patterns could become vulnerable if contract logic changes or in combination with other issues.",
    "Location": "getPartnerCash(), getBeneficiaryCash(), deposit(), setup() functions, and static analysis reentrancy-benign findings"
  }
]