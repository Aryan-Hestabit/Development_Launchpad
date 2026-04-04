const fs = require('fs');

const Test_File = 'Test_File.txt';
const Output_File = 'day1-perf.json';

const results = {};

console.log("Buffer Benchmark:"); 

const bufferStart = Date.now();

fs.readFile(Test_File, (err,data) => {
   if (err) throw err;
   const bufferEnd = Date.now();
   const bufferMemoryUsage = process.memoryUsage();
   
   results.buffer = {
      bytesRead: data.length,
      executionTimeMs: bufferEnd - bufferStart,
      memoryUsageMB: bufferMemoryUsage
   };
});
   console.log("Stream Benchmark:");

   const StreamStart = Date.now()
   let totalBytes = 0;

   const read = fs.createReadStream(Test_File);

   read.on('data', (chunk) => {
      totalBytes += chunk.length;
   });

   read.on('end', () => {
      const StreamEnd = Date.now();
      const StreamMemoryUsage = process.memoryUsage();
   
      results.stream = {
         bytesRead: totalBytes,
         executionTime: StreamEnd - StreamStart,
         memoryUsageMB: StreamMemoryUsage
      };

      fs.writeFileSync(Output_File, JSON.stringify(results,null,2));
      console.log("Benchmark results saved");
   });

   read.on('error', (err) => {
      console.error("Stream error:", err);
   });
