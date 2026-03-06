[
  {
    "Issue": "Owner Transfer Function is Private",
    "Severity": "High",
    "Description": "The transferOwnership function in Ownable contract is declared as private, preventing any actual ownership transfer. This appears in the smart contract code only.",
    "Impact": "Contract ownership cannot be transferred, violating the intended functionality and potentially locking administrative privileges permanently.",
    "Location": "Ownable.transferOwnership(address) function (line with 'private' modifier)"
  },
  {
    "Issue": "Incorrect Ownership Modifier Implementation",
    "Severity": "High",
    "Description": "The onlyOwner modifier in Ownable contract checks against newComer instead of _owner. This appears in the smart contract code only.",
    "Impact": "Access control is broken, allowing unauthorized addresses to call restricted functions, potentially leading to privilege escalation.",
    "Location": "Ownable.onlyOwner modifier (condition 'newComer == _msgSender()')"
  },
  {
    "Issue": "Potential Integer Overflow in setFeeBotTransfer",
    "Severity": "Medium",
    "Description": "The setFeeBotTransfer function uses .add without upper bound checks, which could lead to integer overflow. This appears in the smart contract code only.",
    "Impact": "If called with large values, could cause total supply overflow, breaking token economics and potentially allowing unauthorized minting.",
    "Location": "PETSUINU.setFeeBotTransfer(uint256) function (_tTotal.add(amount) operation)"
  },
  {
    "Issue": "Shadowed Local Variables",
    "Severity": "Low",
    "Description": "Local variables 'owner' in allowance and _approve functions shadow the owner() function from Ownable. This appears in both the smart contract code and static analysis results.",
    "Impact": "Reduces code clarity and may lead to confusion, though no direct security impact.",
    "Location": "PETSUINU.allowance() and _approve() functions (parameter naming), confirmed by static analysis shadowing-local findings"
  },
  {
    "Issue": "Missing Events for Critical Parameters",
    "Severity": "Low",
    "Description": "Functions setMaxBotFee and setMinBotFee change critical parameters without emitting events. This appears in both the smart contract code and static analysis results.",
    "Impact": "Reduces transparency and makes off-chain tracking of parameter changes difficult.",
    "Location": "PETSUINU.setMaxBotFee() and setMinBotFee() functions, confirmed by static analysis events-maths findings"
  },
  {
    "Issue": "Inconsistent Transfer Amount Restriction Logic",
    "Severity": "Medium",
    "Description": "The transfer restriction in _transfer function uses a hardcoded value (100) without context of decimals, potentially being too restrictive. This appears in the smart contract code only.",
    "Impact": "May block legitimate transfers if sender balance is within bot fee range, causing functional issues.",
    "Location": "PETSUINU._transfer() function (require(amount < 100, ...))"
  },
  {
    "Issue": "Unused State Variables and Functions",
    "Severity": "Low",
    "Description": "The contract contains unused variables (newComer in Ownable) and inherited functions (e.g., from Address library) that are never utilized. This appears in the smart contract code only.",
    "Impact": "Increases contract size and gas costs without providing functionality, reducing code efficiency.",
    "Location": "Ownable.newComer variable and various inherited library functions"
  }
]