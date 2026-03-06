[
  {
    "Issue": "Controlled Array Length",
    "Severity": "High",
    "Description": "This issue appears in both the static analysis results and the smart contract code. The CrowdWallet contract allows user-controlled values to push new entries into arrays without bounds checking, which could lead to denial-of-service through gas exhaustion.",
    "Impact": "An attacker could repeatedly call deposit() or withdraw() to grow the arrays indefinitely, potentially making the contract unusable due to excessive gas costs.",
    "Location": "CrowdWallet.deposit() and CrowdWallet.withdraw() functions; Static analysis finding: controlled-array-length"
  },
  {
    "Issue": "Divide Before Multiply Precision Loss",
    "Severity": "Medium",
    "Description": "This issue appears in both the static analysis results and the smart contract code. The calculatePayoutForAddress function performs division before multiplication, which can lead to precision loss and incorrect payout calculations.",
    "Impact": "Token holders may receive incorrect payout amounts due to rounding errors, potentially leading to loss of funds or unfair distribution.",
    "Location": "CrowdWallet.calculatePayoutForAddress() function; Static analysis finding: divide-before-multiply"
  },
  {
    "Issue": "Reentrancy Vulnerability",
    "Severity": "Medium",
    "Description": "This issue appears in the static analysis results only. The withdraw() function makes external calls before updating state variables, creating a potential reentrancy vulnerability despite not transferring ETH before state updates.",
    "Impact": "Although no direct ETH transfer occurs before state changes, cross-function reentrancy could potentially be exploited to manipulate contract state.",
    "Location": "Static analysis finding: reentrancy-no-eth in CrowdWallet.withdraw()"
  },
  {
    "Issue": "Missing Ownership Transfer Events",
    "Severity": "Low",
    "Description": "This issue appears in both the static analysis results and the smart contract code. The transferOwnership function changes the owner state variable without emitting an event, reducing transparency.",
    "Impact": "Off-chain monitoring systems cannot track ownership changes, reducing accountability and transparency.",
    "Location": "Ownable.transferOwnership() function; Static analysis finding: events-access"
  },
  {
    "Issue": "Missing Zero Address Checks",
    "Severity": "Low",
    "Description": "This issue appears in both the static analysis results and the smart contract code. Constructor functions lack zero address validation for owner parameters, which could lead to contract ownership being assigned to invalid addresses.",
    "Impact": "If owner is set to address(0), the contract may become unusable as onlyOwner modifiers would prevent all operations.",
    "Location": "GenesisToken.GenesisToken() and CrowdWallet.CrowdWallet() constructors; Static analysis finding: missing-zero-check"
  },
  {
    "Issue": "Timestamp Dependency",
    "Severity": "Low",
    "Description": "This issue appears in both the static analysis results and the smart contract code. The contract uses block timestamps for critical payout period logic, which can be minimally manipulated by miners.",
    "Impact": "Miners could potentially manipulate payout timing by a few seconds, though the impact is limited given the 30-day payout periods.",
    "Location": "CrowdWallet.isAddressLocked() and CrowdWallet.isNewPayoutPeriod() functions; Static analysis finding: timestamp"
  },
  {
    "Issue": "Missing Configuration Change Events",
    "Severity": "Low",
    "Description": "This issue appears in the static analysis results only. The setBlocksPerPayPeriod function changes a critical configuration parameter without emitting an event.",
    "Impact": "Off-chain systems cannot track changes to the payout period configuration, reducing transparency.",
    "Location": "Static analysis finding: events-maths in CrowdWallet.setBlocksPerPayPeriod()"
  }
]