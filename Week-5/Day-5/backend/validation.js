const Joi = require("joi");

exports.productSchema = Joi.object({
  name: Joi.string().min(3).max(100).required(),
  price: Joi.number().positive().required(),
  description: Joi.string().max(1000).allow(""),
  category: Joi.string().min(1).max(100).required(),
  quantity: Joi.number().integer().min(0).required()
});
