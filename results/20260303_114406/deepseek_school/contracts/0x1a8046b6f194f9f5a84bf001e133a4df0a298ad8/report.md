[
  {
    "Issue": "Potential Signature Malleability in ERC721 Implementation",
    "Severity": "Low",
    "Description": "This issue appears in the smart contract code only. The ERC721 implementation inherits from OpenZeppelin but doesn't include the latest security patches for signature malleability protection that were added in later versions.",
    "Impact": "Could allow for signature replay attacks if signature-based functions are implemented in derived contracts, though the current contract doesn't use signatures directly.",
    "Location": "ERC721 inheritance throughout MinionYachtClub contract"
  },
  {
    "Issue": "abi.encodePacked Collision Vulnerability",
    "Severity": "High",
    "Description": "This issue appears in both the smart contract code and static analysis results. The tokenURI function uses abi.encodePacked with multiple dynamic arguments which could lead to hash collisions.",
    "Impact": "Potential for token URI manipulation or unexpected behavior when generating token URIs, could be exploited to create misleading metadata.",
    "Location": "MinionYachtClub.tokenURI() function - string(abi.encodePacked(currentBaseURI, _tokenId.toString(), uriSuffix))"
  },
  {
    "Issue": "Local Variable Shadowing",
    "Severity": "Low",
    "Description": "This issue appears in both the smart contract code and static analysis results. The walletOfOwner function parameter _owner shadows the Ownable._owner state variable.",
    "Impact": "Could cause confusion in code maintenance and potential bugs if the state variable is accidentally used instead of the parameter, though no immediate security risk.",
    "Location": "MinionYachtClub.walletOfOwner(address _owner) function"
  },
  {
    "Issue": "Potential Integer Overflow in Supply Tracking",
    "Severity": "Medium",
    "Description": "This issue appears in the smart contract code only. While Counters library uses unchecked arithmetic, the maxSupply check prevents overflow, but the implementation relies on proper validation.",
    "Impact": "If maxSupply validation is bypassed or incorrectly implemented, could lead to supply inflation beyond intended limits.",
    "Location": "MinionYachtClub.mint() function and supply counter usage"
  },
  {
    "Issue": "Lack of Reentrancy Protection",
    "Severity": "Medium",
    "Description": "This issue appears in the smart contract code only. The contract uses .call for withdrawals without reentrancy guards, though the withdrawal function is onlyOwner protected.",
    "Impact": "Potential reentrancy attacks if the contract interacts with untrusted contracts in the future, though currently limited to owner-only functions.",
    "Location": "MinionYachtClub.withdraw() function - payable(owner()).call{value: address(this).balance}('')"
  }
]