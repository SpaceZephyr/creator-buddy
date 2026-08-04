const https = require("https");
const querystring = require("querystring");
const constants = require("../config/constants");

async function request(options, data = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(
      { ...options, timeout: constants.REQUEST_TIMEOUT },
      (res) => {
        let body = "";
        res.on("data", (chunk) => {
          body += chunk;
        });
        res.on("end", () => {
          if (res.statusCode !== 200) {
            reject(new Error(`请求失败，状态码: ${res.statusCode}`));
            return;
          }
          try {
            const jsonBody = JSON.parse(body);
            if (jsonBody.errcode === 0) {
              resolve(jsonBody);
            } else {
              reject(new Error(jsonBody.errmsg || "请求失败"));
            }
          } catch (error) {
            reject(new Error(`JSON 解析失败: ${error.message}`));
          }
        });
      },
    );
    req.on("error", reject);
    req.on("timeout", () => {
      req.destroy();
      reject(new Error("请求超时"));
    });
    if (data) {
      req.write(data);
    }
    req.end();
  });
}

async function postJson(path, params, data) {
  const fullPath = `${path}?${querystring.stringify(params)}`;
  return request(
    {
      host: constants.GUAIKEI_BASE_URL,
      path: fullPath,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(JSON.stringify(data)),
      },
    },
    JSON.stringify(data),
  );
}

async function getJson(path, params) {
  const fullPath = `${path}?${querystring.stringify(params)}`;
  return request({
    host: constants.GUAIKEI_BASE_URL,
    path: fullPath,
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
}

module.exports = {
  getJson,
  postJson,
};
