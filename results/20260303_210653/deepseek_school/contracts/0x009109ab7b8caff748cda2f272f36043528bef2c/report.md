[
  {
    "Issue": "Missing Zero-Address Checks in AdminVault Role Changes",
    "Severity": "Medium",
    "Description": "The AdminVault contract's changeOwner and changeAdmin functions lack zero-address validation, allowing privileged roles to be set to address(0). This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Permanent loss of administrative control if roles are accidentally or maliciously set to address(0), potentially bricking the contract system.",
    "Location": "AdminVault.sol: changeOwner() and changeAdmin() functions; Static Analysis: missing-zero-check findings"
  },
  {
    "Issue": "Timestamp Dependency in Contract Change Approvals",
    "Severity": "Medium",
    "Description": "DFSRegistry's approveContractChange and approveWaitPeriodChange functions use block.timestamp for timing checks without SafeMath protection. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Potential for premature approval of contract changes if block timestamps are manipulated, allowing unauthorized contract upgrades.",
    "Location": "DFSRegistry.sol: approveContractChange() and approveWaitPeriodChange(); Static Analysis: timestamp findings"
  },
  {
    "Issue": "Arbitrary ERC20 TransferFrom in TokenUtils",
    "Severity": "Medium",
    "Description": "TokenUtils.pullTokensIfNeeded uses transferFrom with arbitrary _from address without proper origin validation. This issue appears in both the smart contract code and the static analysis results.",
    "Impact": "Potential unauthorized token transfers if calling contracts don't properly validate the _from parameter, could lead to token theft.",
    "Location": "TokenUtils.sol: pullTokensIfNeeded(); Static Analysis: arbitrary-send-erc20 finding"
  },
  {
    "Issue": "Checks-Effects-Interactions Pattern Violation",
    "Severity": "Medium",
    "Description": "Multiple functions (withdrawStuckFunds, pullTokensIfNeeded) violate the checks-effects-interactions pattern by performing external calls before state updates. This issue appears in the smart contract code only.",
    "Impact": "Increased reentrancy risk if state modifications are added later, potential for fund loss or state inconsistency.",
    "Location": "AdminAuth.sol: withdrawStuckFunds(); TokenUtils.sol: pullTokensIfNeeded()"
  },
  {
    "Issue": "Reentrancy Vulnerability in WETH Withdrawal",
    "Severity": "Medium",
    "Description": "TokenUtils.withdrawWeth function can be re-entered via fallback function when ETH is received. This issue appears in the smart contract code only.",
    "Impact": "Enables reentrancy attacks into calling contracts, potential manipulation of contract state and fund theft.",
    "Location": "TokenUtils.sol: withdrawWeth() function"
  },
  {
    "Issue": "Incorrect ERC20 Interface Implementation",
    "Severity": "Medium",
    "Description": "IWETH interface has incorrect ERC20 function signatures. This issue appears in the static analysis results only.",
    "Impact": "Potential compatibility issues with standard ERC20 tokens, may cause function call failures.",
    "Location": "Static Analysis: erc20-interface finding"
  }
]