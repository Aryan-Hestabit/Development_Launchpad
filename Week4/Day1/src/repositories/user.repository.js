const User = require("../models/User");

class UserRepository {
  create(data) {
    return User.create(data);
  }

  findById(id) {
    return User.findById(id);
  }

  find(query = {}) {
    return User.find(query);
  }

  update(id, data) {
    return User.findByIdAndUpdate(id, data, { new: true });
  }

  delete(id) {
    return User.findByIdAndDelete(id);
  }
}

module.exports = new UserRepository();
