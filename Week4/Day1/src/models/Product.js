const mongoose = require("mongoose");

const ProductSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true },
    description: { type: String, trim: true },
    price: { type: Number, required: true, min: 0 },
    ratingSum: { type: Number, default: 0 },
    ratingCount: { type: Number, default: 0 },
    tags: [{ type: String }],
    status: {
      type: String,
      enum: ["active", "inactive"],
      default: "active",
    },
    deletedAt: { type: Date, default: null },
  },
  { timestamps: true, toJSON: { virtuals: true } },
);

ProductSchema.index({ status: 1, createdAt: -1 });

ProductSchema.virtual("rating").get(function () {
  if (!this.ratingCount) return 0;
  return Number((this.ratingSum / this.ratingCount).toFixed(2));
});

module.exports = mongoose.model("Product", ProductSchema);
