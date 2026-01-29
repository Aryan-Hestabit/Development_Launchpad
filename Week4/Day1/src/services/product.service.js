const repository = require("../repositories/product.repository");
const AppError = require("../utils/appError");

class ProductService {
  create(data) {
    return repository.create(data);
  }

  getAll(query) {
    return repository.find(query);
  }

  async getById(id, includeDeleted) {
    const product = await repository.findById(id, includeDeleted);
    if (!product) {
      throw new AppError("Product not found", 404, "PRODUCT_NOT_FOUND");
    }
    return product;
  }

  async delete(id) {
    const product = await repository.softDelete(id);
    if (!product) {
      throw new AppError("Product not found", 404, "PRODUCT_NOT_FOUND");
    }
    return product;
  }
}

module.exports = new ProductService();
