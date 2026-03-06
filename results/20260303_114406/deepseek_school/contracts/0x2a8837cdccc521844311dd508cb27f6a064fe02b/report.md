[
  {
    "Issue": "Exponentiation Overflow Vulnerability in getDivisor",
    "Severity": "High",
    "Description": "The exponentiation operation '10 ** uint256(decimals)' can overflow if token decimals exceed 77, causing transaction reverts and denial-of-service. This issue appears in the smart contract code only.",
    "Impact": "Complete denial-of-service for tokens with excessive decimals, preventing protocol functionality that relies on divisor calculations",
    "Location": "Utils.getDivisor() function, line with exponentiation operation"
  },
  {
    "Issue": "Missing Input Validation for External Calls",
    "Severity": "Medium",
    "Description": "External calls to token registry and global config lack validation of contract existence and input parameters, potentially causing unexpected reverts. This issue appears in the smart contract code only.",
    "Impact": "Denial-of-service if external dependencies are unavailable or malicious, disrupting protocol operations",
    "Location": "All external calls in _isETH() and getDivisor() functions"
  },
  {
    "Issue": "Front-running Vulnerability via Token Decimal Manipulation",
    "Severity": "Medium",
    "Description": "The getDivisor function relies on external token registry calls that could be manipulated via front-running attacks. This issue appears in the smart contract code only.",
    "Impact": "Potential financial losses in integrating contracts due to manipulated divisor calculations for critical operations",
    "Location": "Utils.getDivisor() function, ITokenRegistry external call"
  },
  {
    "Issue": "Unsafe uint8 to uint256 Cast Without Bounds Checking",
    "Severity": "Medium",
    "Description": "While the casting itself is safe, the lack of bounds checking for the decimal value enables the exponentiation overflow vulnerability. This issue appears in the smart contract code only.",
    "Impact": "Enables the exponentiation overflow vulnerability by allowing excessively high decimal values",
    "Location": "Utils.getDivisor() function, uint256 cast operation"
  }
]