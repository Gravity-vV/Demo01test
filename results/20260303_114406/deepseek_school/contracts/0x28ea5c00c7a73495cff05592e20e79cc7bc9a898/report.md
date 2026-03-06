[
  {
    "Issue": "ERC-20 Transfer Arbitrary From Vulnerability",
    "Severity": "High",
    "Description": "The mintToMultipleERC20 and mintToMultipleERC20AL functions use transferFrom with an arbitrary _to address as the from parameter, allowing potential token theft if the contract is maliciously manipulated. This issue appears in the smart contract code and was identified in the static analysis results.",
    "Impact": "An attacker could potentially transfer tokens from any address that has approved this contract, leading to loss of user funds.",
    "Location": "RamppERC721A.mintToMultipleERC20() and RamppERC721A.mintToMultipleERC20AL() functions"
  },
  {
    "Issue": "Reentrancy in Withdraw Function",
    "Severity": "High",
    "Description": "The _withdrawAllSurcharges function contains a reentrancy vulnerability where state variables are updated after external calls. This issue was identified in the static analysis results.",
    "Impact": "An attacker could potentially re-enter the contract during withdrawal and manipulate contract state, potentially leading to fund loss.",
    "Location": "WithdrawableV2._withdrawAllSurcharges() function"
  },
  {
    "Issue": "Unchecked ERC-20 Transfer Return Value",
    "Severity": "High",
    "Description": "The withdrawERC20 function does not check the return value of the ERC-20 transfer call, which could lead to silent failures. This issue was identified in the static analysis results.",
    "Impact": "Failed token transfers would go undetected, potentially leading to loss of tokens.",
    "Location": "WithdrawableV2.withdrawERC20() function"
  },
  {
    "Issue": "Cross-function Reentrancy in Minting",
    "Severity": "Medium",
    "Description": "Multiple minting functions contain potential reentrancy vulnerabilities where state variables are updated after external calls. This issue was identified in the static analysis results.",
    "Impact": "An attacker could potentially re-enter the contract during minting operations and manipulate contract state.",
    "Location": "RamppERC721A.mintToMultipleERC20() and RamppERC721A.mintToMultipleERC20AL() functions"
  },
  {
    "Issue": "Missing Event Emission for Critical State Change",
    "Severity": "Low",
    "Description": "The setRamppAddress function changes a critical contract address without emitting an event, reducing transparency. This issue was identified in the static analysis results.",
    "Impact": "Lack of event emission makes it difficult to track important contract state changes off-chain.",
    "Location": "WithdrawableV2.setRamppAddress() function"
  },
  {
    "Issue": "Potential Integer Overflow in Token Calculations",
    "Severity": "Low",
    "Description": "The contract performs arithmetic operations that could potentially overflow if not properly bounded, though current implementations appear safe. This is a general pattern consideration.",
    "Impact": "If not properly handled, integer overflows could lead to incorrect token calculations and potential fund loss.",
    "Location": "Multiple arithmetic operations throughout the contract code"
  }
]