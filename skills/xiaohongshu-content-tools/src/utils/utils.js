/**
 * 通用工具函数模块
 */

function printBanner() {
  console.log("╔════════════════════════════════════════════╗");
  console.log("║                                            ║");
  console.log("║       📕 小红书运营全链路数据工具           ║");
  console.log("║                                            ║");
  console.log("╚════════════════════════════════════════════╝");
  console.log("");
}

function printLog(level, message) {
  const colorMap = {
    INFO: "\x1b[34m",
    SUCCESS: "\x1b[32m",
    WARN: "\x1b[33m",
    ERROR: "\x1b[31m",
  };
  console.log(
    `${colorMap[level] || ""}[${new Date().toLocaleString()}] [${level}] ${message}\x1b[0m`,
  );
}

module.exports = {
  printBanner,
  printInfo: (msg) => printLog("INFO", msg),
  printSuccess: (msg) => printLog("SUCCESS", msg),
  printError: (msg) => printLog("ERROR", msg),
  printWarn: (msg) => printLog("WARN", msg),
};
