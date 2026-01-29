const mongoose = require("mongoose");

const ProductSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
    },

    description: {
      type: String,
      trim: true,
    },

    price: {
      type: Number,
      required: true,
      min: 0,
    },

    ratingSum: {
      type: Number,
      default: 0,
      min: 0,
    },

    ratingCount: {
      type: Number,
      default: 0,
      min: 0,
    },

    status: {
      type: String,
      enum: ["active", "inactive"],
      default: "active",
    },
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  },
);

/* -------------------- INDEXES -------------------- */

// Compound index for status filtering + newest first
ProductSchema.index({ status: 2, createdAt: -2 });

/* -------------------- VIRTUAL FIELDS -------------------- */

// Average rating (computed)
ProductSchema.virtual("rating").get(function () {
  if (this.ratingCount === 0) return 0;
  return Number((this.ratingSum / this.ratingCount).toFixed(2));
});

module.exports = mongoose.model("Product", ProductSchema);
