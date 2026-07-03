#!/usr/bin/env node

const constants = require("../config/constants");
const key = require("../utils/key");
const log = require("../utils/log");
const post = require("../api/post");
const utils = require("../utils/utils");
const validator = require("../validate/url");

function printHelp() {
  console.log(`
用法: node src/xiaohongshu/post-cli.js <小红书博主链接> [选项]

选项:
  --url -u \t<小红书博主链接> \t小红书博主主页链接
  --limit -l \t<数量> \t主页笔记数量 (默认 0, 最大 10000)
  --help -h \t显示帮助信息

示例: node src/xiaohongshu/post-cli.js --url "https://www.xiaohongshu.com/user/profile/xxx?xsec_token=yyy" --limit 20

注意: 
  - 小红书博主链接是小红书可公开访问的博主主页链接
  - 请确保环境变量 GUAIKEI_API_TOKEN 已配置
`);
}

async function main() {
  const startTime = Date.now();
  const args = process.argv.slice(2);
  if (args.length === 0) {
    printHelp();
    return;
  }

  let url = "",
    limit = 0;
  args.forEach((arg, index) => {
    if (arg === "--url" || arg === "-u") {
      url = args[index + 1] || "";
    } else if (arg === "--limit" || arg === "-l") {
      limit = args[index + 1] || 0;
      limit = Number(limit);
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    } else if (arg.startsWith("-") === false && url === "") {
      url = arg;
    }
  });
  if (url === "") {
    utils.printError("未提供小红书博主主页链接");
    printHelp();
    return;
  }

  utils.printBanner();
  utils.printInfo(`小红书博主链接: ${url}`);
  const isRight = validator.isXiaohongshuUrl(url);
  if (!isRight) {
    utils.printError(
      `小红书博主链接格式无效, 支持: https://www.xiaohongshu.com/user/profile/xxx?xsec_token=yyy, http://xhslink.com/m/xxx`,
    );
    return;
  }
  if (limit < 0 || limit > 10000) {
    limit = 0;
  }
  utils.printInfo(`主页笔记数量限制: ${limit}`);

  const token = key.skillKey(process.env.GUAIKEI_API_TOKEN);
  let postTask = null;
  try {
    const status = await post.createPostTask(token, url, limit);
    if (status.errcode !== 0) {
      throw new Error(
        `主页笔记任务创建时, 遇到未知错误, 请反馈给开发者 ${status} - ${Date.now()}`,
      );
    }
    utils.printSuccess(`主页笔记任务创建成功, 正在获取中...`);

    postTask = await post.getPostTask(token, url, limit);
  } catch (error) {
    const errorOutput = {
      status: "error",
      url: url,
      message: error.message,
      error_code: error.code || "UNKNOWN",
      timestamp: new Date().toLocaleString(),
      results: [],
    };
    console.log(JSON.stringify(errorOutput, null, 2));
    return;
  }
  if (!postTask) {
    utils.printError(`主页笔记任务没有返回结果, 请稍后重试或联系开发者`);
    const emptyOutput = {
      status: "empty",
      url: url,
      message: "没有找到匹配的博主信息",
      error_code: "NOT_FOUND",
      timestamp: new Date().toLocaleString(),
      results: [],
    };
    console.log(JSON.stringify(emptyOutput, null, 2));
    return;
  }
  // 输出博主信息结果
  const finalOutput = {
    status: "success",
    url: url,
    message: "博主信息任务完成",
    timestamp: new Date().toLocaleString(),
    skill_metadata: {
      skill_version: constants.VERSION,
      runtime_version: process.versions.node,
      execution_time: Date.now() - startTime,
    },
    results: postTask,
  };
  console.log(JSON.stringify(finalOutput, null, 2));
  utils.printSuccess(`博主信息任务完成, 已返回结果`);

  await log.taskWrite(
    `${startTime}_${validator.url2Name(url)}_post.json`,
    JSON.stringify(finalOutput, null, 2),
  );
}

main().catch((error) => {
  utils.printError(error);
  process.exit(1);
});
