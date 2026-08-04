const https = require("https");
const { spawnSync } = require("child_process");
const guaikei = require("./guaikei");

function commandExists(command) {
  const result = spawnSync("sh", ["-lc", `command -v ${command}`], {
    encoding: "utf8",
  });
  return result.status === 0;
}

function runCommand(command, args, options = {}) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    timeout: options.timeout || 120000,
    maxBuffer: options.maxBuffer || 20 * 1024 * 1024,
  });

  if (result.error) {
    throw new Error(`${command} 执行失败: ${result.error.message}`);
  }
  if (result.status !== 0) {
    throw new Error(
      `${command} 返回非 0 状态: ${result.status}\n${result.stderr || result.stdout}`,
    );
  }
  return (result.stdout || "").trim();
}

function getDoctor() {
  if (!commandExists("agent-reach")) {
    return {};
  }
  try {
    return JSON.parse(runCommand("agent-reach", ["doctor", "--json"]));
  } catch (error) {
    return { error: error.message };
  }
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    https
      .get(
        url,
        {
          headers: {
            "User-Agent":
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            Referer: "https://www.bilibili.com/",
          },
        },
        (res) => {
          let body = "";
          res.on("data", (chunk) => {
            body += chunk;
          });
          res.on("end", () => {
            try {
              resolve(JSON.parse(body));
            } catch (error) {
              reject(new Error(`JSON 解析失败: ${error.message}`));
            }
          });
        },
      )
      .on("error", reject);
  });
}

function extractXhsNoteId(url) {
  const match = String(url).match(/explore\/([A-Za-z0-9]+)/);
  return match ? match[1] : url;
}

function extractXhsUserId(url) {
  const match = String(url).match(/profile\/([A-Za-z0-9]+)/);
  return match ? match[1] : url;
}

function extractBvid(input) {
  const match = String(input).match(/BV[A-Za-z0-9]+/);
  return match ? match[0] : input;
}

function extractBiliMid(input) {
  const match = String(input).match(/space\.bilibili\.com\/(\d+)/);
  return match ? match[1] : input;
}

function platformError(platform, doctor) {
  if (platform === "xiaohongshu") {
    const message =
      doctor.xiaohongshu && doctor.xiaohongshu.message
        ? doctor.xiaohongshu.message
        : "未发现小红书可用后端。请安装 Agent Reach 的 OpenCLI 渠道并在 Chrome 登录小红书，或配置 xiaohongshu-mcp。";
    return new Error(
      `${message}\n\n兜底方案：配置 GUAIKEI_API_TOKEN 后可使用 Guaikei API 继续搜索小红书公开数据。`,
    );
  }
  if (platform === "douyin") {
    return new Error(
      "Agent Reach 当前未暴露抖音后端。可设置 DOUYIN_COMMAND 指向自定义只读 CLI，或等待 Agent Reach 增加 douyin channel。",
    );
  }
  return new Error(`暂不支持平台: ${platform}`);
}

function runCustomDouyin(action, value, options) {
  const command = process.env.DOUYIN_COMMAND;
  if (!command) {
    throw platformError("douyin", {});
  }
  const args = [action, value];
  if (options.limit) {
    args.push("--limit", String(options.limit));
  }
  return {
    backend: "custom-douyin-command",
    raw: runCommand(command, args),
  };
}

async function searchXiaohongshu(keyword, options = {}) {
  const doctor = getDoctor();
  const active = doctor.xiaohongshu && doctor.xiaohongshu.active_backend;

  if (active === "OpenCLI" && commandExists("opencli")) {
    return {
      backend: "opencli xiaohongshu",
      raw: runCommand("opencli", ["xiaohongshu", "search", keyword, "-f", "yaml"]),
    };
  }
  if (active === "xiaohongshu-mcp" && commandExists("mcporter")) {
    return {
      backend: "xiaohongshu-mcp",
      raw: runCommand("mcporter", [
        "call",
        `xiaohongshu.search_feeds(keyword: ${JSON.stringify(keyword)})`,
        "--timeout",
        "120000",
      ]),
    };
  }
  if (active && active.includes("xhs-cli") && commandExists("xhs")) {
    return {
      backend: "xhs-cli",
      raw: runCommand("xhs", ["search", keyword]),
    };
  }
  try {
    return await guaikei.search(keyword, options);
  } catch (error) {
    if ((process.env.GUAIKEI_API_TOKEN || "").trim()) {
      throw error;
    }
    throw platformError("xiaohongshu", doctor);
  }
}

async function detailXiaohongshu(url, options) {
  const doctor = getDoctor();
  const active = doctor.xiaohongshu && doctor.xiaohongshu.active_backend;

  if (active === "OpenCLI" && commandExists("opencli")) {
    const chunks = [
      runCommand("opencli", ["xiaohongshu", "note", url, "-f", "yaml"]),
    ];
    if (options.limit && Number(options.limit) > 0) {
      chunks.push(
        runCommand("opencli", [
          "xiaohongshu",
          "comments",
          extractXhsNoteId(url),
          "-f",
          "yaml",
        ]),
      );
    }
    return {
      backend: "opencli xiaohongshu",
      raw: chunks.join("\n\n--- comments ---\n\n"),
    };
  }
  if (active === "xiaohongshu-mcp" && commandExists("mcporter")) {
    const noteId = extractXhsNoteId(url);
    const tokenMatch = String(url).match(/[?&]xsec_token=([^&]+)/);
    if (!tokenMatch) {
      throw new Error("xiaohongshu-mcp 读取详情需要包含 xsec_token 的完整笔记 URL。");
    }
    return {
      backend: "xiaohongshu-mcp",
      raw: runCommand("mcporter", [
        "call",
        `xiaohongshu.get_feed_detail(feed_id: ${JSON.stringify(noteId)}, xsec_token: ${JSON.stringify(tokenMatch[1])})`,
        "--timeout",
        "120000",
      ]),
    };
  }
  if (active && active.includes("xhs-cli") && commandExists("xhs")) {
    return {
      backend: "xhs-cli",
      raw: runCommand("xhs", ["read", url]),
    };
  }
  try {
    return await guaikei.detail(url, options || {});
  } catch (error) {
    if ((process.env.GUAIKEI_API_TOKEN || "").trim()) {
      throw error;
    }
    throw platformError("xiaohongshu", doctor);
  }
}

async function userXiaohongshu(url, options = {}) {
  const doctor = getDoctor();
  const active = doctor.xiaohongshu && doctor.xiaohongshu.active_backend;

  if (active === "OpenCLI" && commandExists("opencli")) {
    return {
      backend: "opencli xiaohongshu",
      raw: runCommand("opencli", [
        "xiaohongshu",
        "user",
        extractXhsUserId(url),
        "-f",
        "yaml",
      ]),
    };
  }
  try {
    return await guaikei.user(url, options);
  } catch (error) {
    if ((process.env.GUAIKEI_API_TOKEN || "").trim()) {
      throw error;
    }
    throw platformError("xiaohongshu", doctor);
  }
}

async function searchBilibili(keyword, options) {
  const limit = String(Math.min(Number(options.limit || 20), 50));
  if (commandExists("bili")) {
    return {
      backend: "bili-cli",
      raw: runCommand("bili", ["search", keyword, "--type", "video", "-n", limit]),
    };
  }
  if (commandExists("opencli")) {
    return {
      backend: "opencli bilibili",
      raw: runCommand("opencli", ["bilibili", "search", keyword, "-f", "yaml"]),
    };
  }

  const url =
    "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=" +
    encodeURIComponent(keyword) +
    "&page=1";
  const data = await getJson(url);
  if (data && data.data && Array.isArray(data.data.result)) {
    data.data.result = data.data.result.slice(0, Number(limit));
  }
  return {
    backend: "bilibili-public-api",
    raw: JSON.stringify(data, null, 2),
  };
}

async function detailBilibili(input) {
  const bvid = extractBvid(input);
  if (commandExists("bili")) {
    return {
      backend: "bili-cli",
      raw: runCommand("bili", ["video", bvid]),
    };
  }
  if (commandExists("opencli")) {
    return {
      backend: "opencli bilibili",
      raw: runCommand("opencli", ["bilibili", "video", bvid, "-f", "yaml"]),
    };
  }
  const data = await getJson(
    "https://api.bilibili.com/x/web-interface/view?bvid=" +
      encodeURIComponent(bvid),
  );
  return {
    backend: "bilibili-public-api",
    raw: JSON.stringify(data, null, 2),
  };
}

async function userBilibili(input, options) {
  const mid = extractBiliMid(input);
  if (commandExists("bili")) {
    return {
      backend: "bili-cli",
      raw: runCommand("bili", ["user", mid]),
    };
  }
  throw new Error(
    `B站用户作品需要 bili-cli 或 OpenCLI 支持。当前只解析到用户 ID: ${mid}`,
  );
}

async function search(platform, keyword, options = {}) {
  if (platform === "xiaohongshu" || platform === "xhs") {
    return searchXiaohongshu(keyword, options);
  }
  if (platform === "bilibili" || platform === "bili" || platform === "b站") {
    return searchBilibili(keyword, options);
  }
  if (platform === "douyin" || platform === "抖音") {
    return runCustomDouyin("search", keyword, options);
  }
  throw platformError(platform, {});
}

async function detail(platform, url, options = {}) {
  if (platform === "xiaohongshu" || platform === "xhs") {
    return detailXiaohongshu(url, options);
  }
  if (platform === "bilibili" || platform === "bili" || platform === "b站") {
    return detailBilibili(url, options);
  }
  if (platform === "douyin" || platform === "抖音") {
    return runCustomDouyin("detail", url, options);
  }
  throw platformError(platform, {});
}

async function user(platform, url, options = {}) {
  if (platform === "xiaohongshu" || platform === "xhs") {
    return userXiaohongshu(url, options);
  }
  if (platform === "bilibili" || platform === "bili" || platform === "b站") {
    return userBilibili(url, options);
  }
  if (platform === "douyin" || platform === "抖音") {
    return runCustomDouyin("user", url, options);
  }
  throw platformError(platform, {});
}

module.exports = {
  search,
  detail,
  user,
};
