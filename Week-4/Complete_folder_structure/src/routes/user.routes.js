const express = require("express");
const controller = require("../controllers/user.controller");
const validate = require("../middlewares/validate");
const userSchema = require("../validators/user.schema");

const router = express.Router();

router.post("/", validate(userSchema), controller.create);
router.get("/:id", controller.getById);

module.exports = router;
