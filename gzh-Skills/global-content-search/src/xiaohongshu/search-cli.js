#!/usr/bin/env node

const constants = require("../config/constants");
const log = require("../utils/log");
const utils = require("../utils/utils");
const { parseArgs, pick } = require("../utils/args");
const platformClient = require("../platforms/agentReach");

function printHelp() {
  console.log(`
用法: node src/xiaohongshu/search-cli.js <关键词> [选项]

选项:
  --platform -p <平台>    xiaohongshu, bilibili, douyin。默认 xiaohongshu
  --keyword -k <关键词>   搜索关键词
  --type -t <类型>        兼容旧参数，部分平台可能忽略
  --sort -s <排序>        兼容旧参数，部分平台可能忽略
  --time -i <时间>        兼容旧参数，部分平台可能忽略
  --limit -l <数量>       搜索数量，默认 20
  --output -o <格式>      json, raw。默认 json
  --help -h              显示帮助信息

示例:
  node src/xiaohongshu/search-cli.js -k "AI 编程"
  node src/xiaohongshu/search-cli.js --platform bilibili --keyword "AI 编程" --limit 10
  node src/xiaohongshu/search-cli.js --platform douyin --keyword "AI 编程"

说明:
  - 小红书通过 Agent Reach 检测到的 OpenCLI / xiaohongshu-mcp / xhs-cli 后端访问。
  - B站优先使用 bili-cli / OpenCLI，缺省时使用 B站公开搜索 API。
  - 抖音当前需要设置 DOUYIN_COMMAND 指向本地只读 CLI；Agent Reach 暂未提供抖音 channel。
  - 默认优先使用 Agent Reach；Agent Reach 小红书后端不可用时，可配置 GUAIKEI_API_TOKEN 兜底。
`);
}

async function main() {
  const startTime = Date.now();
  const parsed = parseArgs(process.argv.slice(2));
  if (parsed["--help"] || parsed["-h"] || process.argv.length <= 2) {
    printHelp();
    return;
  }

  const platform = pick(parsed, ["--platform", "-p"], "xiaohongshu");
  const keyword = pick(parsed, ["--keyword", "-k"], parsed._[0] || "");
  const type = Number(pick(parsed, ["--type", "-t"], 0));
  const sort = Number(pick(parsed, ["--sort", "-s"], 0));
  const time = Number(pick(parsed, ["--time", "-i"], 0));
  const limit = Number(pick(parsed, ["--limit", "-l"], 20));
  const output = pick(parsed, ["--output", "-o"], "json");

  if (!keyword) {
    utils.printError("未提供关键词");
    printHelp();
    return;
  }

  utils.printBanner();
  utils.printInfo(`平台: ${platform}`);
  utils.printInfo(`关键词: ${keyword}`);
  utils.printInfo(`数量: ${limit}`);

  try {
    const result = await platformClient.search(platform, keyword, {
      type,
      sort,
      time,
      limit,
    });
    const finalOutput = {
      status: "success",
      platform,
      backend: result.backend,
      keyword,
      limit,
      timestamp: new Date().toLocaleString(),
      skill_metadata: {
        skill_version: constants.VERSION,
        runtime_version: process.versions.node,
        execution_time: Date.now() - startTime,
      },
      raw: result.raw,
    };

    if (output === "raw") {
      console.log(result.raw);
    } else {
      console.log(JSON.stringify(finalOutput, null, 2));
    }

    await log.taskWrite(
      `${startTime}_${platform}_${keyword}_${limit}_search.json`,
      JSON.stringify(finalOutput, null, 2),
    );
  } catch (error) {
    console.log(
      JSON.stringify(
        {
          status: "error",
          platform,
          keyword,
          message: error.message,
          timestamp: new Date().toLocaleString(),
          results: [],
        },
        null,
        2,
      ),
    );
  }
}

main().catch((error) => {
  utils.printError(error.message || error);
  process.exit(1);
});
