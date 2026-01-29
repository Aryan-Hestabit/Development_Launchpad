const Product = require("../models/Product");

class ProductRepository {
  create(data) {
    return Product.create(data);
  }

  findById(id, includeDeleted = false) {
    return Product.findOne({
      _id: id,
      ...(includeDeleted ? {} : { deletedAt: null }),
    });
  }

  find(queryOptions) {
    const {
      search,
      minPrice,
      maxPrice,
      tags,
      sort,
      page = 1,
      limit = 10,
      includeDeleted,
    } = queryOptions;

    const query = {};
    if (!includeDeleted) query.deletedAt = null;

    if (search) {
      query.$or = [
        { name: new RegExp(search, "i") },
        { description: new RegExp(search, "i") },
      ];
    }

    if (minPrice || maxPrice) {
      query.price = {};
      if (minPrice) query.price.$gte = Number(minPrice);
      if (maxPrice) query.price.$lte = Number(maxPrice);
    }

    if (tags) query.tags = { $in: tags.split(",") };

    let mongoQuery = Product.find(query);

    if (sort) {
      const [field, order] = sort.split(":");
      mongoQuery = mongoQuery.sort({ [field]: order === "desc" ? -1 : 1 });
    }

    return mongoQuery
      .skip((page - 1) * limit)
      .limit(Number(limit));
  }

  softDelete(id) {
    return Product.findByIdAndUpdate(
      id,
      { deletedAt: new Date() },
      { new: true }
    );
  }
}

module.exports = new ProductRepository();
