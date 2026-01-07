const fs = require("fs");
const path = require("path");
const { Worker } = require("worker_threads");

function parseArgs() {
  const args = process.argv.slice(2);
  const config = {};

  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].replace("--", "");
      const value =
        args[i + 1] && !args[i + 1].startsWith("--")
          ? args[++i]
          : true;
      config[key] = value;
    }
  }
  return config;
}

const args = parseArgs();
if (!args.file) {
  console.error("Wrong Command");
  process.exit(1);
}

const FILE = args.file;
const TOP_N = Number(args.top || 10);
const MIN_LEN = Number(args.minLen || 1);

const text = fs.readFileSync(FILE, "utf-8");

const allWords = text.toLowerCase().split(/\s+/).filter(w => w.length >= MIN_LEN);

function runWorkers(words, concurrency) {
  const chunkSize = Math.ceil(words.length / concurrency);
  const chunks = [];

  for (let i = 0; i < concurrency; i++) {
    chunks.push(words.slice(i * chunkSize, (i + 1) * chunkSize));
  }

  const workers = chunks.map(chunk => {
    return new Promise((resolve, reject) => {
      const worker = new Worker(path.join(__dirname, "worker.js"));
      worker.postMessage({ words: chunk });

      worker.on("message", resolve);
      worker.on("error", reject);
    });
  });

  return Promise.all(workers);
}

async function main() {
  const perfSummary = [];
  let finalStats = null;

  for (const concurrency of [1, 4, 8]) {
    const start = Date.now();
    const results = await runWorkers(allWords, concurrency);

    const globalFreq = {};
    const globalUnique = new Set();

    let totalWords = 0;
    let longestWord = "";
    let shortestWord = null;

    for (const r of results) {
      totalWords += r.totalWords;

      for (const word in r.freq) {
        globalFreq[word] = (globalFreq[word] || 0) + r.freq[word];
      }

      for (const w in r.unique){
         globalUnique.add(w);
      };

      if (r.longestWord.length > longestWord.length) {
        longestWord = r.longestWord;
      }

      if (!shortestWord || r.shortestWord.length < shortestWord.length) {
        shortestWord = r.shortestWord;
      }
    }

    const sorted = Object.entries(globalFreq)
      .sort((a, b) => b[1] - a[1]);

    const executionTime = Date.now() - start;

    perfSummary.push({ concurrency, executionTime });

    if (concurrency === 8) {
      finalStats = {
        totalWords,
        uniqueWords: globalUnique.size,
        longestWord,
        shortestWord,
        topWords: sorted.slice(0, TOP_N)
      };
    }

    console.log("Concurrency", concurrency, "completed.");
  }

  fs.writeFileSync("stats.json", JSON.stringify(finalStats, null, 2));
  fs.writeFileSync("perf-summary.json", JSON.stringify(perfSummary, null, 2));

  console.log("\n Output file generated:");
}

main();

