const searchApi = require("../api/search");
const detailApi = require("../api/detail");
const postApi = require("../api/post");

function getToken() {
  const token = (process.env.GUAIKEI_API_TOKEN || "").trim();
  if (!token) {
    throw new Error(
      "Agent Reach 当前没有可用的小红书后端。若要使用 Guaikei API 兜底，请配置环境变量 GUAIKEI_API_TOKEN 后重试。",
    );
  }
  if (!/^[0-9a-fA-F]{32}$/.test(token)) {
    throw new Error(
      "GUAIKEI_API_TOKEN 格式不正确，应为 32 位十六进制字符串。请检查后重试。",
    );
  }
  return token;
}

async function search(keyword, options = {}) {
  const token = getToken();
  const type = Number(options.type || 0);
  const sort = Number(options.sort || 0);
  const time = Number(options.time || 0);
  const limit = Number(options.limit || 20);
  const status = await searchApi.createSearchTask(
    token,
    keyword,
    type,
    sort,
    time,
    limit,
  );
  if (status.errcode !== 0) {
    throw new Error("Guaikei 搜索任务创建失败");
  }
  const data = await searchApi.getSearchTask(
    token,
    keyword,
    type,
    sort,
    time,
    limit,
  );
  return {
    backend: "guaikei-api",
    raw: JSON.stringify(data, null, 2),
  };
}

async function detail(url, options = {}) {
  const token = getToken();
  const limit = Number(options.limit || 0);
  const status = await detailApi.createDetailTask(token, url, limit);
  if (status.errcode !== 0) {
    throw new Error("Guaikei 详情任务创建失败");
  }
  const data = await detailApi.getDetailTask(token, url, limit);
  return {
    backend: "guaikei-api",
    raw: JSON.stringify(data, null, 2),
  };
}

async function user(url, options = {}) {
  const token = getToken();
  const limit = Number(options.limit || 20);
  const status = await postApi.createPostTask(token, url, limit);
  if (status.errcode !== 0) {
    throw new Error("Guaikei 博主作品任务创建失败");
  }
  const data = await postApi.getPostTask(token, url, limit);
  return {
    backend: "guaikei-api",
    raw: JSON.stringify(data, null, 2),
  };
}

module.exports = {
  search,
  detail,
  user,
};
