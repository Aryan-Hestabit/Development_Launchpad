const express = require("express");
const mongoose = require("mongoose");
const instanceId = process.env.HOSTNAME;

const app = express();
app.use(express.json());

mongoose.connect(process.env.MONGO_URL, {
  serverSelectionTimeoutMS: 5000
})
.then(() => {
  console.log("✅ MongoDB connected successfully");
})
.catch(err => {
  console.error("❌ MongoDB connection error:", err.message);
  process.exit(1);
});


const Product = mongoose.model("Product", {
  name: String,
  price: Number,
  description: String,
  category: String,
  quantity: Number
});

app.get("/health", (req, res) => res.send("OK"));
app.use("/api", require("./routes")(Product, instanceId));

app.listen(3000, () => console.log("Backend running"));
