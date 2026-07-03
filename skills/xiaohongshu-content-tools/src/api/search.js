/**
 * 小红书笔记搜索模块
 */
const constants = require("../config/constants");
const { postJson, getJson } = require("../utils/request");
const { withRetry } = require("../utils/retry");
const utils = require("../utils/utils");

/**
 * 创建小红书笔记搜索任务
 * @param {string} token - API令牌
 * @param {string} keyword - 搜索关键词
 * @param {number} type - 内容类型, 0: 全部, 1: 视频, 2: 图文
 * @param {number} sort - 排序规则, 0: 综合, 1: 最新, 2: 最多点赞, 3: 最多评论, 4: 最多收藏
 * @param {number} time - 发布时间, 0: 全部, 1: 一天内, 2: 一周内, 3: 半年内
 * @param {number} limit - 搜索数量, 1-10000
 * @returns {Promise<Object>} 搜索任务状态
 * @throws {Error} API调用失败时抛出错误
 */
async function createSearchTask(token, keyword, type, sort, time, limit) {
  return await withRetry(
    async () => {
      return await postJson(
        "/api/xiaohongshu/note-search/keyword",
        { _: Date.now(), token: token },
        { keyword, type, sort, time, limit },
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
 * 获取小红书笔记搜索任务结果
 * @param {string} token - API令牌
 * @param {string} keyword - 搜索关键词
 * @param {number} type - 内容类型, 0: 全部, 1: 视频, 2: 图文
 * @param {number} sort - 排序规则, 0: 综合, 1: 最新, 2: 最多点赞, 3: 最多评论, 4: 最多收藏
 * @param {number} time - 发布时间, 0: 全部, 1: 一天内, 2: 一周内, 3: 半年内
 * @param {number} limit - 搜索数量, 1-10000
 * @returns {Promise<Array>} 搜索结果数组
 * @throws {Error} API调用失败时抛出错误
 */
async function getSearchTask(token, keyword, type, sort, time, limit) {
  return await withRetry(
    async () => {
      const res = await getJson("/api/xiaohongshu/note-search/info", {
        _: Date.now(),
        token: token,
        keyword,
        type,
        sort,
        time,
        limit,
      });
      if (res.errcode === 0) {
        for (let i = 0; i < res.data.length; i++) {
          const item = res.data[i];
          if (item.id && item.xsec_token) {
            res.data[i].url =
              "https://www.xiaohongshu.com/explore/" +
              item.id +
              "?xsec_token=" +
              item.xsec_token;
          }
          if (item.user && item.user.user_id && item.user.xsec_token) {
            res.data[i].user.url =
              "https://www.xiaohongshu.com/user/profile/" +
              item.user.user_id +
              "?xsec_token=" +
              item.user.xsec_token;
          } else if (item.user && item.user.user_id) {
            res.data[i].user.url =
              "https://www.xiaohongshu.com/user/profile/" + item.user.user_id;
          }
        }
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
  createSearchTask,
  getSearchTask,
};
