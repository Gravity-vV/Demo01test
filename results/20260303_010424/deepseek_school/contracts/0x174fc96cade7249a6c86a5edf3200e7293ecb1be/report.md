```json
[
  {
    "Issue": "Reentrancy Vulnerability in withdraw() Function",
    "Severity": "High",
    "Description": "Critical reentrancy vulnerability found in the smart contract code where the withdraw() function performs external token transfers before updating any state variables, violating the Checks-Effects-Interactions pattern. This appears in the smart contract code only.",
    "Impact": "Complete drainage of all reserve tokens from the treasury through recursive reentrancy attacks, leading to total fund loss and contract compromise.",
    "Location": "TestTreasury.withdraw() function, line ~145, IERC20(_token).safeTransfer() call"
  },
  {
    "Issue": "Reentrancy Vulnerability in manage() Function",
    "Severity": "High",
    "Description": "Critical reentrancy vulnerability found in the smart contract code where the manage() function performs external token transfers without state updates, allowing reentrancy attacks. This appears in the smart contract code only.",
    "Impact": "Complete drainage of treasury funds as attackers can recursively call manage() during token transfer callbacks, stealing all reserve tokens.",
    "Location": "TestTreasury.manage() function, line ~151, IERC20(_token).safeTransfer() call"
  },
  {
    "Issue": "Violation of Checks-Effects-Interactions Pattern",
    "Severity": "High",
    "Description": "Multiple functions in the smart contract code violate the CEI pattern by performing external interactions before state updates, creating reentrancy vulnerabilities. This appears in the smart contract code only.",
    "Impact": "Enables reentrancy attacks across multiple functions, allowing complete fund drainage and contract compromise.",
    "Location": "withdraw() and manage() functions in TestTreasury contract"
  },
  {
    "Issue": "Access Control Vulnerability in pullManagement()",
    "Severity": "High",
    "Description": "Critical access control vulnerability found in the smart contract code where pullManagement() function lacks the onlyPolicy modifier, allowing unauthorized ownership transfer. This appears in the smart contract code only.",
    "Impact": "Complete loss of contract ownership to unauthorized parties, enabling attackers to drain all funds and modify all access controls.",
    "Location": "Ownable.pullManagement() function, line ~47-52, missing onlyPolicy modifier"
  },
  {
    "Issue": "Privilege Escalation in Role Management",
    "Severity": "High",
    "Description": "Critical privilege escalation vulnerability found in the smart contract code where the toggle() function allows the policy owner to assign themselves any privileged role without restrictions. This appears in the smart contract code only.",
    "Impact": "Complete bypass of intended access controls, allowing the owner to grant themselves all roles and drain the treasury.",
    "Location": "TestTreasury.toggle() function, no validation against self-assignment"
  },
  {
    "Issue": "Precision Loss in Token Valuation",
    "Severity": "Medium",
    "Description": "Precision loss vulnerability found in the smart contract code where valueOfToken() function truncates fractional values during division operations, especially for tokens with decimals > 9. This appears in the smart contract code only.",
    "Impact": "Incorrect token valuation leading to economic inefficiencies, underreporting of reserve values, and potential financial miscalculations.",
    "Location": "TestTreasury.valueOfToken() function, line with division operation: _amount.mul(10**9).div(10**decimals)"
  },
  {
    "Issue": "Missing Internal Accounting System",
    "Severity": "Medium",
    "Description": "Design flaw found in the smart contract code where the treasury lacks internal balance tracking, relying solely on actual token balances which enables reentrancy attacks. This appears in the smart contract code only.",
    "Impact": "Enables reentrancy attacks and makes proper CEI pattern implementation impossible, compromising contract security.",
    "Location": "TestTreasury contract missing reserveTokenBalance mapping and corresponding accounting logic"
  }
]
```