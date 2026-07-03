/**
 * 小红书笔记详情和评论模块
 */
const constants = require("../config/constants");
const { postJson, getJson } = require("../utils/request");
const { withRetry } = require("../utils/retry");
const utils = require("../utils/utils");

/**
 * 创建小红书笔记详情及评论任务
 * @param {string} token - API令牌
 * @param {string} url - 笔记链接
 * @param {number} limit - 评论数量, 1-10000
 * @returns {Promise<Object>} 详情任务状态
 * @throws {Error} API调用失败时抛出错误
 */
async function createDetailTask(token, url, limit) {
  return await withRetry(
    async () => {
      return await postJson(
        "/api/xiaohongshu/detail/url",
        { _: Date.now(), token: token },
        { url: url, limit: limit },
      );
    },
    constants.CREATE_MAX_ATTEMPTS,
    (attempt, err) => {
      utils.printError(
        `【创建任务重试】 ${attempt + 1}/${constants.CREATE_MAX_ATTEMPTS} 次 - ${err.message}`,
      );
    },
  );
}

/**
 * 获取小红书笔记详情及评论任务结果
 * @param {string} token - API令牌
 * @param {string} url - 笔记链接
 * @param {number} limit - 评论数量, 1-10000
 * @returns {Promise<Object>} 详情结果对象
 * @throws {Error} API调用失败时抛出错误
 */
async function getDetailTask(token, url, limit) {
  return await withRetry(
    async () => {
      const res = await getJson("/api/xiaohongshu/detail/info", {
        _: Date.now(),
        token: token,
        url: url,
        limit: limit,
      });
      if (res.errcode === 0) {
        if (res.data.id && res.data.xsec_token) {
          res.data.url =
            "https://www.xiaohongshu.com/explore/" +
            res.data.id +
            "?xsec_token=" +
            res.data.xsec_token;
        }
        if (
          res.data.user &&
          res.data.user.user_id &&
          res.data.user.xsec_token
        ) {
          res.data.user.url =
            "https://www.xiaohongshu.com/user/profile/" +
            res.data.user.user_id +
            "?xsec_token=" +
            res.data.user.xsec_token;
        }
        return res.data;
      } else {
        throw new Error(`请求错误信息: ${res.errmsg || "请求失败"}`);
      }
      return null;
    },
    constants.QUERY_MAX_ATTEMPTS,
    (attempt, err) => {
      utils.printError(
        `【查询任务重试】 ${attempt + 1}/${constants.QUERY_MAX_ATTEMPTS} 次 - ${err.message}`,
      );
    },
  );
}

module.exports = {
  createDetailTask,
  getDetailTask,
};
