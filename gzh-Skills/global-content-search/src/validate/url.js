const utils = require("../utils/utils");

/**
 * 检查小红书链接是否符合要求
 */
function isXiaohongshuUrl(url) {
  url = url.trim();
  url = url.replace("http://", "https://");
  if (url.indexOf("https://") !== 0) {
    utils.printError(`小红书链接必须以 https:// 开头`);
    return false;
  }
  if (url.indexOf(" ") !== -1) {
    utils.printError(`小红书链接不能包含空格`);
    return false;
  }
  if (url.indexOf("https://www.xiaohongshu.com/explore/") !== -1) {
  } else if (url.indexOf("https://www.xiaohongshu.com/user/profile/") !== -1) {
  } else if (url.indexOf("https://xhslink.com/m/") !== -1) {
  } else {
    return false;
  }
  return true;
}

function url2Name(url) {
  url = url.substring(0, url.indexOf("?"));
  return url
    .replace(/^https?:\/\//, "")
    .replace(/www\.xiaohongshu\.com\/explore\/|xhslink\.com\/m\//, "")
    .replace(/[\/?=&\-]/g, "_");
}

module.exports = {
  isXiaohongshuUrl,
  url2Name,
};
