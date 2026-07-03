const https = require("https");
const querystring = require("querystring");
const constants = require("../config/constants");
const utils = require("./utils");

async function request(options, data = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(
      { ...options, timeout: constants.REQUEST_TIMEOUT },
      (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          if (res.statusCode === 200) {
            const jsonBody = JSON.parse(body);
            if (jsonBody.errcode === 0) {
              resolve(jsonBody);
            } else {
              reject(new Error(jsonBody.errmsg || "请求失败"));
              return;
            }
          } else if (res.statusCode === 401 || res.statusCode === 403) {
            reject(
              new Error(
                `GUAIKEI_API_TOKEN 无效, 请检查环境变量 或 联系微信: 13395823479 获取解决方案`,
              ),
            );
          } else {
            reject(new Error(`请求失败, 状态码: ${res.statusCode}`));
          }
        });
      },
    );
    req.on("error", reject);
    req.on("timeout", () => reject(new Error("请求超时")));
    if (data) req.write(data);
    req.end();
  });
}

async function postJson(path, params, data) {
  const fullPath = `${path}?${querystring.stringify(params)}`;
  const options = {
    host: constants.BASE_URL,
    path: fullPath,
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Content-Length": Buffer.byteLength(JSON.stringify(data)),
    },
  };
  return await request(options, JSON.stringify(data));
}

async function getJson(path, params) {
  const fullPath = `${path}?${querystring.stringify(params)}`;
  const options = {
    host: constants.BASE_URL,
    path: fullPath,
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return await request(options);
}

module.exports = { getJson, postJson };
