import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://hakuai.kr",
  trailingSlash: "always",
  build: { format: "directory" },
});
