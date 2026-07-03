/**
 * 小红书博主详情、已发布笔记模块
 */
const constants = require("../config/constants");
const { postJson, getJson } = require("../utils/request");
const { withRetry } = require("../utils/retry");
const utils = require("../utils/utils");

/**
 * 创建小红书已发布笔记任务
 * @param {string} token - API令牌
 * @param {string} url - 博主URL
 * @param {number} limit - 返回笔记数量
 * @returns  {Promise<Object>} 已发布笔记任务状态
 * @throws {Error} API调用失败时抛出错误
 */
async function createPostTask(token, url, limit) {
  return await withRetry(
    async () => {
      return await postJson(
        "/api/xiaohongshu/post/url",
        { _: Date.now(), token: token },
        { url, limit },
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
 * 获取小红书已发布笔记任务结果
 * @param {string} token - API令牌
 * @param {string} url - 博主URL
 * @param {number} limit - 返回笔记数量
 * @returns {Promise<Object>} 已发布笔记数组
 * @throws {Error} API调用失败时抛出错误
 */
async function getPostTask(token, url, limit) {
  return await withRetry(
    async () => {
      const res = await getJson("/api/xiaohongshu/post/info", {
        _: Date.now(),
        token: token,
        url,
        limit,
      });
      if (res.errcode === 0) {
        return res.data;
      } else {
        throw new Error(`请求错误信息: ${res.errmsg || "请求失败"}`);
      }
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
  createPostTask,
  getPostTask,
};
