const constants = require("../config/constants");

async function withRetry(fn, maxAttempts, errorHandler) {
  let lastError;
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      return await fn(attempt);
    } catch (error) {
      lastError = error;
      if (errorHandler) errorHandler(attempt, error);
      if (attempt < maxAttempts - 1) {
        await new Promise((resolve) =>
          setTimeout(resolve, constants.RETRY_INTERVAL),
        );
      }
    }
  }
  throw lastError || new Error(`重试${maxAttempts}次后失败`);
}

module.exports = { withRetry };
