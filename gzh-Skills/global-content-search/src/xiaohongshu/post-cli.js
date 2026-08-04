#!/usr/bin/env node

const constants = require("../config/constants");
const log = require("../utils/log");
const utils = require("../utils/utils");
const { parseArgs, pick } = require("../utils/args");
const platformClient = require("../platforms/agentReach");

function printHelp() {
  console.log(`
用法: node src/xiaohongshu/post-cli.js <主页链接或ID> [选项]

选项:
  --platform -p <平台>  xiaohongshu, bilibili, douyin。默认 xiaohongshu
  --url -u <主页链接或ID> 创作者主页链接或 ID
  --limit -l <数量>     作品数量，部分后端支持。默认 20
  --output -o <格式>    json, raw。默认 json
  --help -h            显示帮助信息

示例:
  node src/xiaohongshu/post-cli.js --url "https://www.xiaohongshu.com/user/profile/xxx?xsec_token=yyy"
  node src/xiaohongshu/post-cli.js --platform bilibili --url "https://space.bilibili.com/123456"
  node src/xiaohongshu/post-cli.js --platform douyin --url "https://www.douyin.com/user/xxx"

说明:
  - 小红书用户作品目前需要 Agent Reach 的 OpenCLI 小红书后端。
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
  const limit = Number(pick(parsed, ["--limit", "-l"], 20));
  const output = pick(parsed, ["--output", "-o"], "json");

  if (!url) {
    utils.printError("未提供主页链接或 ID");
    printHelp();
    return;
  }

  utils.printBanner();
  utils.printInfo(`平台: ${platform}`);
  utils.printInfo(`主页/用户: ${url}`);
  utils.printInfo(`作品数量限制: ${limit}`);

  try {
    const result = await platformClient.user(platform, url, { limit });
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
      `${startTime}_${platform}_post.json`,
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
