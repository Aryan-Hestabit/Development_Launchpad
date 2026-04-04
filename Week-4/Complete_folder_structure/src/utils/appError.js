class AppError extends Error {
  constructor(message, statusCode = 500, code = "INTERNAL_ERROR") {
    super(message);

    this.statusCode = statusCode;
    this.code = code;

    // Captures correct stack trace (important for debugging)
    Error.captureStackTrace(this, this.constructor);
  }
}

module.exports = AppError;
