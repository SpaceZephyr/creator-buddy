const fs = require("fs");
const path = require("path");
const utils = require("./utils");

async function taskWrite(filename, content) {
  const safeFilename = filename.replace(/[\\/:*?"<>|]/g, "_");
  const outputFilename = path.join(
    path.dirname(__filename),
    "..",
    "..",
    "logs",
    safeFilename,
  );

  try {
    await fs.promises.mkdir(path.dirname(outputFilename), { recursive: true });
    await fs.promises.writeFile(outputFilename, content);
    utils.printSuccess(`  → 已保存到 ${outputFilename}`);
  } catch (error) {
    utils.printError(`日志写入失败: ${error.message}`);
  }
}

module.exports = {
  taskWrite,
};
