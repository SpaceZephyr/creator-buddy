#!/usr/bin/env node

const constants = require("../config/constants");
const log = require("../utils/log");
const utils = require("../utils/utils");
const { parseArgs, pick } = require("../utils/args");
const platformClient = require("../platforms/agentReach");

function printHelp() {
  console.log(`
用法: node src/xiaohongshu/detail-cli.js <链接或ID> [选项]

选项:
  --platform -p <平台>  xiaohongshu, bilibili, douyin。默认 xiaohongshu
  --url -u <链接或ID>   笔记/视频链接或 ID
  --limit -l <数量>     评论数量，部分后端支持。默认 0
  --output -o <格式>    json, raw。默认 json
  --help -h            显示帮助信息

示例:
  node src/xiaohongshu/detail-cli.js --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --limit 20
  node src/xiaohongshu/detail-cli.js --platform bilibili --url "BVxxxx"
  node src/xiaohongshu/detail-cli.js --platform douyin --url "https://www.douyin.com/video/xxx"

说明:
  - 小红书详情仍建议使用搜索结果里的完整 URL，包含 xsec_token。
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
  const url = pick(parsed, ["--url", "-u"], parsed._[0] || "");
  const limit = Number(pick(parsed, ["--limit", "-l"], 0));
  const output = pick(parsed, ["--output", "-o"], "json");

  if (!url) {
    utils.printError("未提供链接或 ID");
    printHelp();
    return;
  }

  utils.printBanner();
  utils.printInfo(`平台: ${platform}`);
  utils.printInfo(`目标: ${url}`);
  utils.printInfo(`评论数量限制: ${limit}`);

  try {
    const result = await platformClient.detail(platform, url, { limit });
    const finalOutput = {
      status: "success",
      platform,
      backend: result.backend,
      url,
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
      `${startTime}_${platform}_detail.json`,
      JSON.stringify(finalOutput, null, 2),
    );
  } catch (error) {
    console.log(
      JSON.stringify(
        {
          status: "error",
          platform,
          url,
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
