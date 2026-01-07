const os = require('os')
const path = require('path');

console.log("OS:", os.type(),os.release());
console.log("Architecture:", os.arch());
console.log("CPU Cores:", os.cpus().length);
console.log("Total Memory:", os.totalmem());
console.log("System Uptime:", os.uptime());
console.log("Current Logged User:", os.userInfo().username);
console.log("Node Path:", process.execPath)
