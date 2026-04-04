const http = require("http");

http.createServer((req, res) => {
  res.end("Secure backend response ");
}).listen(3000, () => {
  console.log("Backend running on port 3000");
});
