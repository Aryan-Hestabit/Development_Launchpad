const http = require("http");
const url = require("url");

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);

  // /echo
  if (parsedUrl.pathname === "/echo") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(req.headers, null, 2));
  }

  // /slow?ms=3000
  else if (parsedUrl.pathname === "/slow") {
    const delay = Number(parsedUrl.query.ms || 1000);
    setTimeout(() => {
      res.writeHead(200);
      res.end(`Delayed response by ${delay}ms`);
    }, delay);
  }

  // /cache
  else if (parsedUrl.pathname === "/cache") {
    res.writeHead(200, {
      "Cache-Control": "public, max-age=60",
      "ETag": "simple-etag-123"
    });
    res.end("Cached response");
  }

  // If head not found throw error
  else {
    res.writeHead(404);
    res.end("Not Found");
  }
});

server.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});
