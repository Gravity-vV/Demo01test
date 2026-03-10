#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"

TEST_VERSIONS=("0.8.20" "0.4.26" "0.6.12" "0.5.17" "0.7.6")

for version in "${TEST_VERSIONS[@]}"; do
    echo "======================================"
    echo "Testing Slither with solc $version"
    solc-select use $version > /dev/null
    
    # Create simple dummy contract
    cat << 'SOLC' > dummy_test_$version.sol
// SPDX-License-Identifier: MIT
pragma solidity >=0.4.0 <0.9.0;
contract Test {
    uint256 public value;
    function setValue(uint256 _v) public { value = _v; }
}
SOLC

    slither dummy_test_$version.sol || true
    echo "--------------------------------------"
done
