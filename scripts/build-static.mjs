import { cp, mkdir, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dist = resolve(projectRoot, "dist");
const portfolio = resolve(dist, "portfolio");

await rm(dist, { recursive: true, force: true });
await mkdir(resolve(dist, "server"), { recursive: true });
await mkdir(resolve(dist, ".openai"), { recursive: true });

await Promise.all([
  cp(resolve(projectRoot, "index.html"), resolve(portfolio, "index.html")),
  cp(resolve(projectRoot, "styles.css"), resolve(portfolio, "styles.css")),
  cp(resolve(projectRoot, "script.js"), resolve(portfolio, "script.js")),
  cp(resolve(projectRoot, "assets"), resolve(portfolio, "assets"), { recursive: true }),
  cp(resolve(projectRoot, ".openai", "hosting.json"), resolve(dist, ".openai", "hosting.json")),
]);

const worker = `export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/" || url.pathname === "/index.html") {
      const target = new URL(request.url);
      target.pathname = "/portfolio/index.html";
      return env.ASSETS.fetch(new Request(target, request));
    }
    return env.ASSETS.fetch(request);
  },
};\n`;

await writeFile(resolve(dist, "server", "index.js"), worker, "utf8");
