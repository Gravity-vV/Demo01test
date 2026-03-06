[
  {
    "Issue": "Reentrancy vulnerability in fund transfer functions",
    "Severity": "High",
    "Description": "Multiple functions transfer ETH before updating state variables, violating checks-effects-interactions pattern. Issue appears in the smart contract code only.",
    "Impact": "Complete drainage of contract funds through recursive reentrancy attacks, theft of all player deposits and winnings",
    "Location": "pullShares() function (line ~184), clear() function (line ~283), airDrop() function (line ~196)"
  },
  {
    "Issue": "Integer overflow/underflow vulnerabilities in arithmetic operations",
    "Severity": "High",
    "Description": "Multiple arithmetic operations performed without overflow protection. Issue appears in the smart contract code only.",
    "Impact": "Incorrect token/share calculations, potential fund loss or manipulation, contract state corruption",
    "Location": "processKick() function, setShares() function, storeWinnerShare() function, kickerCount increments"
  },
  {
    "Issue": "Insecure access control mechanisms",
    "Severity": "High",
    "Description": "Multiple functions lack proper access control, including unrestricted ownership transfer and unprotected critical functions. Issue appears in the smart contract code only.",
    "Impact": "Unauthorized fund transfers, contract manipulation, privilege escalation, permanent contract control takeover",
    "Location": "changeOwner(), changeHouseAddress(), WithdrawFromKickTheCoin.release(), setKtcAddress() functions"
  },
  {
    "Issue": "Unchecked external calls with potential fund loss",
    "Severity": "High",
    "Description": "Multiple .transfer() calls without success/failure checking. Issue appears in the smart contract code only.",
    "Impact": "Permanent fund loss when transfers fail after state changes, locked contract balances, failed payouts to legitimate recipients",
    "Location": "pullShares(), airDrop(), clear(), release() functions across all contracts"
  },
  {
    "Issue": "Front-running vulnerability in commission reward mechanism",
    "Severity": "Medium",
    "Description": "Predictable first and second kicker rewards create economic incentive for front-running. Issue appears in the smart contract code only.",
    "Impact": "Commission rewards systematically captured by front-runners, unfair playing field, reduced legitimate participation",
    "Location": "processKick() function (lines ~237-250), setShares() function (lines ~224-232)"
  },
  {
    "Issue": "Block number manipulation vulnerability in game timing",
    "Severity": "Medium",
    "Description": "Game logic relies on block.number for critical timing mechanisms. Issue appears in the smart contract code only.",
    "Impact": "Miners could influence game outcomes, manipulation of sundown grace period timing, unfair advantage to miner-participants",
    "Location": "kickTheCoin(), isGameActive(), sundown(), clear() functions using block.number comparisons"
  },
  {
    "Issue": "Incorrect winner share calculation and distribution",
    "Severity": "Medium",
    "Description": "storeWinnerShare() function incorrectly awards entire pot to last player instead of proper commission distribution. Issue appears in the smart contract code only.",
    "Impact": "Unfair distribution depriving legitimate commission recipients, undermines game economic model, potential financial losses",
    "Location": "storeWinnerShare() private function"
  },
  {
    "Issue": "State transition race condition vulnerability",
    "Severity": "Medium",
    "Description": "Non-atomic state transition between game phases allows manipulation. Issue appears in the smart contract code only.",
    "Impact": "Legitimate winners denied winnings, attackers can reset game to prevent payouts, funds can be locked",
    "Location": "kickTheCoin(), hasWinner(), isGameActive() functions interaction"
  },
  {
    "Issue": "Missing input validation for critical parameters",
    "Severity": "Medium",
    "Description": "Multiple functions lack zero-address validation and parameter bounds checking. Issue appears in the smart contract code only.",
    "Impact": "Critical addresses could be set to zero permanently locking funds, game parameters could be set to unreasonable values",
    "Location": "changeOwner(), changeHouseAddress(), changeGameParameters(), airDrop() functions"
  },
  {
    "Issue": "Unbounded array growth in factory contract",
    "Severity": "Medium",
    "Description": "Arrays grow indefinitely without pagination or limits. Issue appears in the smart contract code only.",
    "Impact": "Potential gas limit issues, degraded performance, inability to retrieve complete system information",
    "Location": "KickTheCoinFactory games array and founderToCreatedGames mapping"
  }
]