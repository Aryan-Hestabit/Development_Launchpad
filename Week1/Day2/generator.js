const fs = require("fs");

const corpus = ["lorem", "ipsum", "sit", "development", "launchpad",
                "week", "days", "dictionary", "javascript", "python",
                "implement", "concurrency", "chunks", "async"];

const limit = 210000;
let output = [];

for(let i = 0; i < limit; i++) {
   output.push(corpus[Math.floor(Math.random() * corpus.length)]);
}

fs.writeFileSync("Corpus.txt", output.join(" "));
console.log("Sample text file generated");
