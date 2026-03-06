[
  {
    "Issue": "Reentrancy vulnerability in TokenUtils external calls",
    "Severity": "High",
    "Description": "TokenUtils.pullTokensIfNeeded() and withdrawTokens() perform unsafe external calls without reentrancy protection. This appears in both the smart contract code and static analysis results.",
    "Impact": "An attacker could reenter during token transfers to manipulate contract state and potentially drain funds.",
    "Location": "TokenUtils.sol functions pullTokensIfNeeded() and withdrawTokens()"
  },
  {
    "Issue": "Centralized admin control with single-point failure",
    "Severity": "High",
    "Description": "AdminVault and DFSRegistry have highly centralized admin controls without time-locks or multi-sig requirements. This appears in the smart contract code.",
    "Impact": "Compromised admin keys could lead to complete contract takeover, fund loss, or contract freezing.",
    "Location": "AdminVault.sol changeOwner/changeAdmin functions and DFSRegistry.sol admin functions"
  },
  {
    "Issue": "Missing zero address checks in privileged functions",
    "Severity": "Medium",
    "Description": "AdminVault.changeOwner() and changeAdmin() lack zero address validation. This appears in both smart contract code and static analysis results.",
    "Impact": "Admin could accidentally set privileged roles to zero address, permanently locking contract administration.",
    "Location": "AdminVault.sol lines 62-73"
  },
  {
    "Issue": "Unprotected timestamp dependency in wait period checks",
    "Severity": "Medium",
    "Description": "DFSRegistry uses block.timestamp for wait period approvals without minimum time constraints. This appears in both smart contract code and static analysis results.",
    "Impact": "Miners could potentially influence timing of critical contract changes if wait periods are very short.",
    "Location": "DFSRegistry.sol approveContractChange() and approveWaitPeriodChange()"
  },
  {
    "Issue": "Incomplete SafeMath protection in arithmetic operations",
    "Severity": "Medium",
    "Description": "Some arithmetic operations in DFSRegistry and AdminVault don't use SafeMath protections. This appears in the smart contract code.",
    "Impact": "Potential for arithmetic overflows/underflows in critical calculations.",
    "Location": "DFSRegistry.sol wait period calculations and AdminVault.sol storage updates"
  },
  {
    "Issue": "Unbounded wait periods in registry management",
    "Severity": "Low",
    "Description": "DFSRegistry allows setting wait periods without minimum/maximum boundaries. This appears in the smart contract code.",
    "Impact": "Could lead to impractically short security delays or effectively permanent locks on changes.",
    "Location": "DFSRegistry.sol addNewContract() and startWaitPeriodChange()"
  },
  {
    "Issue": "Missing event emission for critical admin changes",
    "Severity": "Low",
    "Description": "AdminVault doesn't emit events for owner/admin changes. This appears in the smart contract code.",
    "Impact": "Lack of transparency and forensic trail for privileged operations.",
    "Location": "AdminVault.sol changeOwner() and changeAdmin()"
  }
]