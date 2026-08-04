const constants = require("../config/constants");
const { postJson, getJson } = require("../utils/request");
const { withRetry } = require("../utils/retry");

async function createDetailTask(token, url, limit) {
  return withRetry(
    () =>
      postJson(
        "/api/xiaohongshu/detail/url",
        { _: Date.now(), token },
        { url, limit },
      ),
    constants.CREATE_MAX_ATTEMPTS,
  );
}

async function getDetailTask(token, url, limit) {
  return withRetry(
    async () => {
      const res = await getJson("/api/xiaohongshu/detail/info", {
        _: Date.now(),
        token,
        url,
        limit,
      });
      if (res.data && res.data.id && res.data.xsec_token) {
        res.data.url = `https://www.xiaohongshu.com/explore/${res.data.id}?xsec_token=${res.data.xsec_token}`;
      }
      if (
        res.data &&
        res.data.user &&
        res.data.user.user_id &&
        res.data.user.xsec_token
      ) {
        res.data.user.url = `https://www.xiaohongshu.com/user/profile/${res.data.user.user_id}?xsec_token=${res.data.user.xsec_token}`;
      }
      return res.data;
    },
    constants.QUERY_MAX_ATTEMPTS,
  );
}

module.exports = {
  createDetailTask,
  getDetailTask,
};
