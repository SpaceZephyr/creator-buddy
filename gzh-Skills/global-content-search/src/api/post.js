const constants = require("../config/constants");
const { postJson, getJson } = require("../utils/request");
const { withRetry } = require("../utils/retry");

async function createPostTask(token, url, limit) {
  return withRetry(
    () =>
      postJson(
        "/api/xiaohongshu/post/url",
        { _: Date.now(), token },
        { url, limit },
      ),
    constants.CREATE_MAX_ATTEMPTS,
  );
}

async function getPostTask(token, url, limit) {
  return withRetry(
    async () => {
      const res = await getJson("/api/xiaohongshu/post/info", {
        _: Date.now(),
        token,
        url,
        limit,
      });
      return res.data;
    },
    constants.QUERY_MAX_ATTEMPTS,
  );
}

module.exports = {
  createPostTask,
  getPostTask,
};
