#!/usr/bin/env node

const constants = require("../config/constants");
const key = require("../utils/key");
const log = require("../utils/log");
const search = require("../api/search");
const utils = require("../utils/utils");
const validator = require("../validate/keyword");

function printHelp() {
  console.log(`
用法: node src/xiaohongshu/search-cli.js <关键词> [选项]

选项:
  --keyword -k \t<关键词> \t搜索关键词
  --type -t \t<类型> \t内容类型, 0: 全部(默认), 1: 视频, 2: 图文
  --sort -s \t<排序> \t排序规则, 0: 综合(默认), 1: 最新, 2: 最多点赞, 3: 最多评论, 4: 最多收藏
  --time -i \t<时间> \t发布时间, 0: 不限(默认), 1: 一天内, 2: 一周内, 3: 半年内
  --limit -l \t<数量> \t搜索数量 (默认 20, 最大 10000)
  --output -o \t<格式> \t输出格式, json, markdown (默认 json)
  --help -h \t显示帮助信息

示例1: node src/xiaohongshu/search-cli.js -k AI
示例2: node src/xiaohongshu/search-cli.js -k "AI 模型"
示例3: node src/xiaohongshu/search-cli.js --keyword AI --type 0 --sort 0 --limit 10 --output json
示例4: node src/xiaohongshu/search-cli.js --keyword "AI 模型" --type 1 --sort 2 --limit 20 --output markdown

注意: 
  - 关键词建议 2-50 个汉字，避免特殊符号
  - 请确保环境变量 GUAIKEI_API_TOKEN 已配置
  - 所有参数都会自动清洗和验证
`);
}

async function main() {
  const startTime = Date.now();
  const args = process.argv.slice(2);
  if (args.length === 0) {
    printHelp();
    return;
  }

  let keyword = "",
    type = 0,
    sort = 0,
    time = 0,
    limit = 20,
    output = "json";
  args.forEach((arg, index) => {
    if (arg === "--keyword" || arg === "-k") {
      keyword = args[index + 1] || "";
    } else if (arg === "--type" || arg === "-t") {
      type = args[index + 1] || 0;
      type = Number(type);
    } else if (arg === "--sort" || arg === "-s") {
      sort = args[index + 1] || 0;
      sort = Number(sort);
    } else if (arg === "--time" || arg === "-i") {
      time = args[index + 1] || 0;
      time = Number(time);
    } else if (arg === "--limit" || arg === "-l") {
      limit = args[index + 1] || 20;
      limit = Number(limit);
    } else if (arg === "--output" || arg === "-o") {
      output = args[index + 1] || "json";
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    } else if (arg.startsWith("-") === false && keyword === "") {
      keyword = arg;
    }
  });
  if (keyword === "") {
    utils.printError(`未提供关键词`);
    printHelp();
    return;
  }

  utils.printBanner();
  utils.printInfo(`原始关键词: ${keyword}`);
  const isRight = validator.isKeywordValid(keyword);
  if (!isRight) {
    return;
  }
  keyword = validator.cleanKeyword(keyword);
  utils.printInfo(`清洗后关键词: ${keyword}`);

  [type, sort, time, limit, output] = validator.optionFormat(
    type,
    sort,
    time,
    limit,
    output,
  );
  utils.printInfo(
    `内容类型: ${type}, 排序规则: ${sort}, 数量: ${limit}, 输出格式: ${output}`,
  );

  const token = key.skillKey(process.env.GUAIKEI_API_TOKEN);
  let searchTask = null;
  try {
    const status = await search.createSearchTask(
      token,
      keyword,
      type,
      sort,
      time,
      limit,
    );
    if (status.errcode !== 0) {
      throw new Error(
        `搜索任务创建时, 遇到未知错误, 请反馈给开发者 ${status} - ${Date.now()}`,
      );
    }
    utils.printSuccess(`搜索任务创建成功, 正在搜索中...`);

    searchTask = await search.getSearchTask(
      token,
      keyword,
      type,
      sort,
      time,
      limit,
    );
  } catch (error) {
    const errorOutput = {
      status: "error",
      keyword: keyword,
      message: error.message,
      error_code: error.code || "UNKNOWN",
      type: type,
      sort: sort,
      time: time,
      limit: limit,
      output_format: output,
      timestamp: new Date().toLocaleString(),
      results: [],
    };
    console.log(JSON.stringify(errorOutput, null, 2));
    return;
  }
  if (!searchTask || !Array.isArray(searchTask) || searchTask.length === 0) {
    utils.printError(`搜索任务没有返回结果, 请稍后重试或联系开发者`);
    const emptyOutput = {
      status: "empty",
      keyword: keyword,
      message: "没有找到匹配的视频或图文内容",
      error_code: "NO_MATCH",
      type: type,
      sort: sort,
      time: time,
      limit: limit,
      output_format: output,
      timestamp: new Date().toLocaleString(),
      results: [],
    };
    console.log(JSON.stringify(emptyOutput, null, 2));
    return;
  }

  // 输出搜索结果
  const finalOutput = {
    status: "success",
    keyword: keyword,
    message: "搜索任务完成",
    type: type,
    sort: sort,
    time: time,
    limit: limit,
    output_format: output,
    total: searchTask.length,
    timestamp: new Date().toLocaleString(),
    skill_metadata: {
      skill_version: constants.VERSION,
      runtime_version: process.versions.node,
      execution_time: Date.now() - startTime,
    },
    results: searchTask,
  };
  if (output === "markdown") {
    const message = validator.formatMessage(keyword, searchTask);
    utils.printInfo(message);
    utils.printSuccess(`搜索任务完成, 共返回 ${finalOutput.total} 条结果`);
  } else {
    console.log(JSON.stringify(finalOutput, null, 2));
    utils.printSuccess(`搜索任务完成, 共返回 ${finalOutput.total} 条结果`);
  }

  await log.taskWrite(
    `${startTime}_${keyword}_${type}_${sort}_${limit}_search.json`,
    JSON.stringify(finalOutput, null, 2),
  );
}

main().catch((error) => {
  utils.printError(error);
  process.exit(1);
});
