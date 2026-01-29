const repository = require("../repositories/user.repository");
const AppError = require("../utils/appError");

class UserService {
  async create(data) {
    return repository.create(data);
  }

  async getById(id) {
    const user = await repository.findById(id);
    if (!user) {
      throw new AppError("User not found", 404, "USER_NOT_FOUND");
    }
    return user;
  }
}

module.exports = new UserService();
