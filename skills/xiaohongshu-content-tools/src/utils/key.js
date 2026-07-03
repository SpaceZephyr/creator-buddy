/**
 * TOKEN管理模块
 */
const utils = require("./utils");

function isValidToken(token) {
  if (!token || typeof token !== "string") {
    return false;
  }

  if (token.length !== 32) {
    return false;
  }

  const hexPattern = /^[0-9a-fA-F]{32}$/;
  return hexPattern.test(token);
}

function skillKey(token) {
  if (!isValidToken(token)) {
    utils.printWarn(
      "警告: 你的 GUAIKEI_API_TOKEN 未配置或已失效,技能功能已暂停服务. \n" +
        "请添加微信: 13395823479,获取专属私有TOKEN,一键配置即可恢复全部功能,永久稳定可用,不影响日常办公!",
    );
    return "";
  }

  utils.printInfo("已使用配置的私有TOKEN");
  return token;
}

module.exports = {
  skillKey,
};
