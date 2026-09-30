// 校验 primer 子集: 模板与生成页中用到的类必须全部保留在 assets/primer-subset.css
// 用法: node scripts/check_primer_subset.js  (在仓库根目录执行)
const fs = require("fs");
const path = require("path");
const ROOT = process.argv[2] || ".";

const orig = fs.readFileSync(path.join(ROOT, "assets/Primer@21.1.1/primer.css"), "utf8");
const sub = fs.readFileSync(path.join(ROOT, "assets/primer-subset.css"), "utf8");

const files = [];
for (const dir of ["templates", "docs", "docs/post"]) {
    const p = path.join(ROOT, dir);
    if (!fs.existsSync(p)) continue;
    for (const f of fs.readdirSync(p)) {
        if (f.endsWith(".html")) files.push(path.join(p, f));
    }
}

const tokens = new Set();
for (const f of files) {
    const s = fs.readFileSync(f, "utf8");
    for (const m of s.matchAll(/class="([^"]*)"/g)) {
        m[1].split(/\s+/).forEach(t => t && tokens.add(t));
    }
}
// 运行时由页面 JS 拼接的类
for (const t of ["Label", "LabelName", "LabelTime", "lists", "SideNav-item", "d-flex",
    "flex-items-center", "flex-justify-between", "AnimatedEllipsis", "Counter", "notFind",
    "listLabels", "listTitle", "genTime"]) {
    tokens.add(t);
}

const has = (css, t) => new RegExp("\\." + t + "(?![\\w-])").test(css);
const missing = [...tokens].filter(t => has(orig, t) && !has(sub, t));
if (missing.length) {
    console.error("子集缺失 " + missing.length + " 个类: " + missing.join(", "));
    process.exit(1);
}
console.log("类校验通过: " + tokens.size + " 个 token 全部覆盖");
