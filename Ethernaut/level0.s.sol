pragma solidity ^0.8.0;

import "../src/level0.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";

contract Solution is Script {
    Instance public ins = Instance(0xB614452c5A1f2c547739fE6D7Ce43a24CD590b92);

    // SPDX-License-Identifier: MIT

    function run() public {
        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        string memory password = ins.password();
        console.log(password);
        ins.authenticate(password);
        vm.stopBroadcast();
    }
}
