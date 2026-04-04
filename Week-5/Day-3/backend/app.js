const http = require("http");
const os = require("os");

const PORT = 3000;

const server = http.createServer((req, res) => {
  res.end(`Response from backend container: ${os.hostname()}\n`);
});

server.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
