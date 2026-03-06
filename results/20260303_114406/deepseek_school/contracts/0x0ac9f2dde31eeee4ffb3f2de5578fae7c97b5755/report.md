[
  {
    "Issue": "Reentrancy Vulnerability in Mint Function",
    "Severity": "High",
    "Description": "The mint function contains external calls (_safeMint) before updating state variables, creating a reentrancy risk. This issue is identified in the static analysis results and confirmed in the smart contract code where _safeMint is called before _tokenInfos is updated.",
    "Impact": "An attacker could re-enter the mint function during token transfer, potentially minting additional tokens without proper payment or manipulating contract state.",
    "Location": "LissajousToken.mint() function and static analysis reentrancy-eth finding"
  },
  {
    "Issue": "Dangerous Strict Equality Checks",
    "Severity": "Medium",
    "Description": "Multiple functions use strict equality checks (==) with modulo operations, which can be vulnerable to manipulation. This issue appears in both the static analysis results and the smart contract code.",
    "Impact": "Strict equality checks with modulo operations can be exploited if attackers can influence the input values, potentially bypassing intended logic.",
    "Location": "LissajousToken.aspectRatio() and isHashRainbow() functions; static analysis incorrect-equality findings"
  },
  {
    "Issue": "Unchecked Return Values from Enumerable Operations",
    "Severity": "Medium",
    "Description": "Multiple functions in the ERC721 implementation ignore return values from EnumerableSet and EnumerableMap operations. This issue is identified in the static analysis results and confirmed in the ERC721 contract code.",
    "Impact": "Ignoring return values from collection operations could lead to silent failures and inconsistent state if operations fail unexpectedly.",
    "Location": "ERC721._mint(), _transfer(), _burn() functions; static analysis unused-return findings"
  },
  {
    "Issue": "Variable Shadowing in Return Parameters",
    "Severity": "Low",
    "Description": "The lissajousArguments function has a local variable that shadows a return parameter name. This issue appears in both the static analysis results and the smart contract code.",
    "Impact": "Variable shadowing can cause confusion and potential logic errors if the wrong variable is referenced in calculations.",
    "Location": "LissajousToken.lissajousArguments() function; static analysis shadowing-local finding"
  },
  {
    "Issue": "Potential Integer Overflow in Price Calculation",
    "Severity": "Medium",
    "Description": "The minPrice function uses multiplication with _priceIncreasePromille (1001) which could potentially overflow for large token indices. This issue is identified through code pattern analysis.",
    "Impact": "For very large token supplies, the price calculation could overflow, causing incorrect pricing logic and potential loss of funds.",
    "Location": "LissajousToken.minPrice() function: return (lastMinPrice * _priceIncreasePromille) / 1000"
  },
  {
    "Issue": "Insufficient Input Validation in Mint Function",
    "Severity": "Medium",
    "Description": "The mint function lacks validation for the 'to' address parameter and doesn't properly handle the rainbow token edge case in batch mints. This issue appears in the smart contract code only.",
    "Impact": "Tokens could be minted to invalid addresses, and rainbow token logic may not behave as intended when minting multiple tokens.",
    "Location": "LissajousToken.mint() function, particularly the rainbow token handling logic"
  }
]