[
  {
    "Issue": "Critical Ownership Function Override",
    "Severity": "High",
    "Description": "The owner() function in the Ownable contract always returns address(0) instead of the actual owner address, breaking external ownership verification while internal onlyOwner checks still work. This appears in the smart contract code only.",
    "Impact": "External systems cannot verify ownership, potentially preventing legitimate contract management and causing integration failures with wallets, explorers, and DeFi protocols.",
    "Location": "Ownable contract, owner() function at line ~273"
  },
  {
    "Issue": "Unrestricted Token Minting Capability",
    "Severity": "High",
    "Description": "The setFeeTotal function allows the owner to mint unlimited additional tokens without any supply cap constraints. This appears in the smart contract code only.",
    "Impact": "Owner can arbitrarily inflate token supply, potentially devaluing all existing holdings and enabling complete economic control over the token.",
    "Location": "MIONA contract, setFeeTotal() function"
  },
  {
    "Issue": "Inverted Transfer Restriction Logic",
    "Severity": "High",
    "Description": "The transfer restriction condition uses incorrect logic (sender != _tBlackAddress) that allows blacklisted addresses to bypass restrictions. This appears in the smart contract code only.",
    "Impact": "Blacklisted addresses can freely transfer to restricted destinations, completely negating the intended blacklist functionality.",
    "Location": "MIONA contract, _transfer() function, condition at line ~424"
  },
  {
    "Issue": "Reentrancy Vulnerability in Transfer Function",
    "Severity": "Medium",
    "Description": "The _transfer function emits Transfer event before completing all state updates, potentially allowing reentrancy through event monitoring. This appears in the smart contract code only.",
    "Impact": "Malicious contracts could exploit the inconsistent state during event emission to perform reentrancy attacks and manipulate contract state.",
    "Location": "MIONA contract, _transfer() function, emit Transfer before state completion"
  },
  {
    "Issue": "Missing Zero-Address Validation",
    "Severity": "Medium",
    "Description": "setBlackListBot and setBlackAddress functions lack zero-address checks, allowing critical addresses to be set to address(0). This appears in both smart contract code and static analysis results.",
    "Impact": "Owner could accidentally or maliciously disable blacklist functionality by setting addresses to zero, compromising security mechanisms.",
    "Location": "MIONA contract, setBlackListBot() and setBlackAddress() functions; Static analysis finding: missing-zero-check"
  },
  {
    "Issue": "Front-running Vulnerability in Approval Mechanism",
    "Severity": "Medium",
    "Description": "Standard ERC-20 approval race condition exists without increaseAllowance/decreaseAllowance pattern protection. This appears in the smart contract code patterns only.",
    "Impact": "Malicious spenders can front-run approval transactions to extract up to 2x the intended allowance amount from users.",
    "Location": "MIONA contract, approve() and transferFrom() functions"
  },
  {
    "Issue": "Missing Events for State Changes",
    "Severity": "Low",
    "Description": "Critical state-changing functions like setMaxTxBlack do not emit events, reducing transparency. This appears in both smart contract code and static analysis results.",
    "Impact": "Lack of event emission makes it difficult to track and audit state changes, reducing contract transparency and monitoring capability.",
    "Location": "MIONA contract, setMaxTxBlack() function; Static analysis finding: events-maths"
  },
  {
    "Issue": "Variable Shadowing",
    "Severity": "Low",
    "Description": "Local variables named 'owner' shadow the owner() function, causing code clarity issues. This appears in both smart contract code and static analysis results.",
    "Impact": "Reduces code readability and maintainability, potentially leading to confusion and bugs during future development.",
    "Location": "MIONA contract, various functions; Static analysis finding: shadowing-local"
  },
  {
    "Issue": "Missing Immutable/Constant Declarations",
    "Severity": "Low",
    "Description": "Token metadata (name, symbol, decimals) and fixed values are stored as regular variables instead of constants/immutables. This appears in the smart contract code only.",
    "Impact": "Gas inefficiency and unnecessary storage usage for values that should be compile-time constants.",
    "Location": "MIONA contract, _name, _symbol, _decimals, _maxBlack variable declarations"
  }
]