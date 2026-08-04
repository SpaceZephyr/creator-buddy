const utils = require("../utils/utils");

/**
 * 检查搜索关键词是否符合要求
 */
function isKeywordValid(keyword) {
  keyword = keyword.trim();
  if (keyword.length < 2) {
    utils.printError(`搜索关键词长度不能小于 2 个字符`);
    return false;
  }
  if (keyword.length > 50) {
    utils.printError(`搜索关键词长度不能超过 50 个字符`);
    return false;
  }
  if (/[<>\"'&]/g.test(keyword)) {
    utils.printError(`搜索关键词包含特殊字符, 请输入普通关键词, 例如: 新媒体`);
    return false;
  }
  if (keyword.includes("http")) {
    utils.printError(
      `搜索关键词包含 http 链接, 请输入普通关键词, 例如: 新媒体`,
    );
    return false;
  }
  return true;
}

/**
 * 清洗搜索关键词
 */
function cleanKeyword(keyword) {
  keyword = keyword.trim();
  return keyword.replace(/[^\u4e00-\u9fa5a-zA-Z0-9\s.,!?# ，。！？]/g, "");
}

/**
 * 格式化搜索选项, 并检查是否有效
 */
function optionFormat(type, sort, time, limit, output) {
  type = type || 0;
  sort = sort || 0;
  time = time || 0;
  limit = limit || 20;
  output = output || "json";
  if (type !== 0 && type !== 1 && type !== 2) {
    utils.printError(`内容类型 ${type} 无效, 请使用 0, 1, 2。 默认值为 0`);
    type = 0;
  }
  if (sort !== 0 && sort !== 1 && sort !== 2 && sort !== 3 && sort !== 4) {
    utils.printError(
      `排序规则 ${sort} 无效, 请使用 0, 1, 2, 3, 4。 默认值为 0`,
    );
    sort = 0;
  }
  if (time !== 0 && time !== 1 && time !== 2 && time !== 3) {
    utils.printError(`发布时间 ${time} 无效, 请使用 0, 1, 2, 3。 默认值为 0`);
    time = 0;
  }
  if (limit < 1 || limit > 10000) {
    utils.printError(`搜索数量 ${limit} 无效, 请使用 1-10000。 默认值为 20`);
    limit = 20;
  }
  if (output !== "json" && output !== "markdown") {
    utils.printError(
      `输出格式 ${output} 无效, 请使用 json, markdown。 默认值为 json`,
    );
    output = "json";
  }
  return [type, sort, time, limit, output];
}

function formatMessage(keyword, result) {
  let message = `### 📊 关于 "${keyword}" 的小红书数据简报\n`;
  message += `共找到 **${result.length}** 条高互动笔记（样本量）。\n\n`;
  message += "#### 🏆 爆款前三名\n";
  result.slice(0, 3).forEach((item, index) => {
    message += `${index + 1}. **[${item.title?.substring(0, 20)}...](${item.url})** `;
    message += `🔥${item.liked_count}点赞 `;
    message += `💬${item.comment_count}评论\n`;
  });
  message += "\n---\n\n";
  message += "#### 📝 详细列表\n";

  message += "-".repeat(35) + "\n\n";
  for (let i = 0; i < result.length; i++) {
    const item = result[i];
    message += `**${i + 1} .** ${item.title || "[无标题]"}\n`;
    message += `**发布时间**: ${item.publish_time || "[未知]"}\n`;
    message += `**链接**: ${item.url || "[未知]"}\n`;
    message += `**发布人**: ${item.user.nickname || "[未知]"}\n`;
    if (item.image_list && item.image_list.length > 0) {
      message += `**图文**: ${item.image_list.slice(0, 3).join(", ")}...\n`;
    }
    message += `**点赞**: ${item.liked_count || 0}\t`;
    message += `**评论**: ${item.comment_count || 0}\t`;
    message += `**收藏**: ${item.collected_count || 0}\t`;
    message += `**分享**: ${item.shared_count || 0}\n`;
    message += "\n";
  }
  message += "-".repeat(35) + "\n";
  message += `**共 ${result.length} 条结果**\n`;
  return message;
}

module.exports = {
  cleanKeyword,
  formatMessage,
  isKeywordValid,
  optionFormat,
};
