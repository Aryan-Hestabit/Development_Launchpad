const express = require("express");
const mongoose = require("mongoose");

const app = express();
const PORT = 5000;

// IMPORTANT: mongo is the SERVICE NAME (not localhost)
mongoose.connect("mongodb://mongo:27017/day2db")
  .then(() => console.log("MongoDB connected"))
  .catch(err => console.error(err));

app.get("/", (req, res) => {
  res.send("Server running & Mongo connected 🚀");
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
