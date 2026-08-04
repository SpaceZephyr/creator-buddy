const constants = require("../config/constants");
const { postJson, getJson } = require("../utils/request");
const { withRetry } = require("../utils/retry");

async function createSearchTask(token, keyword, type, sort, time, limit) {
  return withRetry(
    () =>
      postJson(
        "/api/xiaohongshu/note-search/keyword",
        { _: Date.now(), token },
        { keyword, type, sort, time, limit },
      ),
    constants.CREATE_MAX_ATTEMPTS,
  );
}

async function getSearchTask(token, keyword, type, sort, time, limit) {
  return withRetry(
    async () => {
      const res = await getJson("/api/xiaohongshu/note-search/info", {
        _: Date.now(),
        token,
        keyword,
        type,
        sort,
        time,
        limit,
      });
      for (const item of res.data || []) {
        if (item.id && item.xsec_token) {
          item.url = `https://www.xiaohongshu.com/explore/${item.id}?xsec_token=${item.xsec_token}`;
        }
        if (item.user && item.user.user_id && item.user.xsec_token) {
          item.user.url = `https://www.xiaohongshu.com/user/profile/${item.user.user_id}?xsec_token=${item.user.xsec_token}`;
        } else if (item.user && item.user.user_id) {
          item.user.url = `https://www.xiaohongshu.com/user/profile/${item.user.user_id}`;
        }
      }
      return res.data || [];
    },
    constants.QUERY_MAX_ATTEMPTS,
  );
}

module.exports = {
  createSearchTask,
  getSearchTask,
};
