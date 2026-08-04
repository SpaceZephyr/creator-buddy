function parseArgs(args) {
  const parsed = { _: [] };
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (!arg.startsWith("-")) {
      parsed._.push(arg);
      continue;
    }
    const next = args[i + 1];
    if (next && !next.startsWith("-")) {
      parsed[arg] = next;
      i += 1;
    } else {
      parsed[arg] = true;
    }
  }
  return parsed;
}

function pick(parsed, names, fallback = "") {
  for (const name of names) {
    if (parsed[name] !== undefined) {
      return parsed[name];
    }
  }
  return fallback;
}

module.exports = {
  parseArgs,
  pick,
};
