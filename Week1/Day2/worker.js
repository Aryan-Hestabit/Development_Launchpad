const { parentPort } = require("worker_threads");

parentPort.on("message", ({ words }) => {
  const freq = {};
  const unique = new Set();

  let longestWord = "";
  let shortestWord = words[0] || "";

  for (const word of words) {
    freq[word] = (freq[word] || 0) + 1;
    unique.add(word);

    if (word.length > longestWord.length) {
      longestWord = word;
    }

    if (word.length < shortestWord.length) {
      shortestWord = word;
    }
  }

  parentPort.postMessage({
    totalWords: words.length,
    freq,
    unique: Array.from(unique),
    longestWord,
    shortestWord
  });
});

