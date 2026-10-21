// Pixel Bench: a static, hash-routed site over window.BENCH (written by eval/site.py).
// Pages: home, leaderboard, characters (+ one per character), small sprites, archive, method, skill.
"use strict";
const D = window.BENCH;
const $ = (s) => document.querySelector(s);
const INSTALL = "npx skills add junyudev/pixel-art";
const REPO = "https://github.com/junyudev/pixel-art";
const html = document.documentElement;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

// ---------- copy ----------
const S = {
  en: {
    getSkill: "Get the skill", navBoard: "Leaderboard", navChars: "Characters", navSmall: "Small sprites", navMethod: "Method",
    navSkill: "Skill", eyebrowHome: "Agent skill · benchmark",
    heroA: "Pixel art, ", heroB: "written", heroC: " pixel by pixel.",
    heroLead: "pixel-art is an agent skill that draws sprites as true pixel grids, from 16×16 icons to 64×64 characters. Pixel Bench measures it with blind paired judging, including against real Eastward sprites.",
    stCaption: "The grid route: a palette, one character per pixel, rendered as is.",
    showTitle: "16×16, written as text", showLead: "The same 12 briefs for each model, with the skill and without. With it, the agent writes the grid, renders it and fixes what doesn't read at 1×. All at extra-high effort.",
    noSkill: "no skill", judged: "Blind judging", skillVs: "pixel-art vs no skill", bothSkill: "both with pixel-art",
    conceptTitle: "64×64, from a gpt-image concept", conceptLead: "The concept route: Codex image generation designs the character, a converter recovers the true pixels, and the agent picks, edits and cleans up.",
    conceptA: "gpt-image concept", conceptB: "true pixels",
    reconTitle: "Redrawn from three lines", reconLead: "Real Eastward characters, drawn from a 3–5 sentence brief by an agent that never saw them, then judged blind against the original.",
    vsV12: (w, n) => `vs v12: ${w}–${n - w}`, setSuite: "Benchmark tasks", setShowcase: "Showcase · 16×16", setConcept: "Concept route · 64×64",
    ctaBoard: "See the leaderboard", ctaSkill: "Get the skill",
    stChars: "characters", stEntries: "entries", stTasks: "tasks", stDrawings: "drawings", stJudgings: "judgings",
    original: "original", redrawn: "redrawn", heroCaption: (n, e) => `${n}: the original next to ${e}'s drawing from the brief alone.`,
    charsTitle: "Original vs. redrawn", allChars: "All characters →",
    benchTitle: "The benchmarks", benchLead: "Same brief, same canvas, same reference pack with the target removed, judged against the same rubric.",
    reconName: "Reconstruction", reconDesc: "Redraw 10 real Eastward characters from a short brief. Two blind judges per pair compare each drawing with the original on 7 criteria.",
    smallName: "Small sprites", smallDesc: "16×16 and 32×32 icons and characters with no original: two drawings side by side, judged blind on a 7-point rubric.",
    archiveName: "Archive: early briefs", archiveDesc: "Three invented briefs from the first rounds (v1–v10), judged pairwise with reference sprites but no original.",
    runs: (n) => `${n} judgings`, rating: "Rating", boardTitle: "Leaderboard",
    boardNote: "Rating: a Bradley–Terry fit over every paired judging, on an Elo-like scale where 1000 is the average entry. The bar is a 90 % interval from resampling whole characters. Overlapping bars mean the judges can't tell those entries apart yet.",
    thEntry: "Entry", thRating: "Rating (90 % interval)", thVs: "vs v12", thMean: "Mean /70", thCalls: "Calls", thOut: "Output", thMin: "Minutes", thDrawn: "Drawn",
    histTitle: "Ratings across versions", histNote: "In the order the versions were written. Each new rule set was meant to fix what judges complained about; the ratings stayed within each other's intervals. Dashed lines: the same models with no skill.",
    critTitle: "Scores by criterion", critNote: "Mean score out of 10 over every judging of the entry. Opponents differ between entries, so read rows, not small gaps.",
    costNote: "Cost is the median per drawing: API calls, output tokens and active minutes (interruptions subtracted). The image-gen route also calls an external image model, not counted here.",
    charsLead: "Each character is drawn only from its brief. Held-out characters were chosen after the skill version under test was written.",
    heldout: "held out", brief: "Brief", attemptsTitle: "Every attempt", best: "best", won: "won", notes: "What the judges said was still missing",
    noJudging: "not judged", cost: (c) => `${c.calls} calls · ${Math.round(c.out / 1000)}k out · ${Math.round(c.minutes)} min`,
    smallLead: "Fixed briefs at 16×16 and 32×32 with no original to copy. Each pair of drawings is judged blind by two judges, sides swapped, on readability, silhouette, form, palette, cleanliness, brief and appeal.",
    smallPairs: "Head to head", smallTasks: "Every task", pending: "waiting for results",
    archiveLead: "The first rounds used invented briefs and no original: two versions side by side, judged with reference sprites for style. v1 and v3 predate the judging; v10 was stopped before it.",
    methodTitle: "Method", skillTitle: "The pixel-art skill", copy: "Copy", copied: "Copied",
    installNote: "Works with Claude Code, Codex, Cursor and other agents. The skill needs Python with pillow, numpy and scipy.",
    skillLead: "A Claude Code skill that draws pixel art as real PNGs at any size. It picks a route by canvas size: the construct route is on the leaderboard, the grid route on the small-sprite suite.",
    routes: "Three routes", install: "Install", use: "Use it", results: "How it scores",
    download: "Download zip", github: "GitHub",
    footA: "Explore", footB: "About", footNote: "Code under the MIT license. Eastward © Pixpil; original sprites are shown with permission. Fonts: Press Start 2P, Pixelify Sans, Fusion Pixel (SIL OFL).",
    vsAnchor: (w, n) => `${w}–${n - w}`, of70: "/70", judgedBy: (n) => `${n} judgings`,
  },
  zh: {
    getSkill: "获取技能", navBoard: "排行榜", navChars: "角色", navSmall: "小尺寸", navMethod: "方法", navSkill: "技能",
    eyebrowHome: "agent 技能 · 基准测试",
    heroA: "像素画，", heroB: "一格一格", heroC: "写出来。",
    heroLead: "pixel-art 是一个 agent 技能，把精灵图当作真正的像素网格来画，从 16×16 图标到 64×64 角色。Pixel Bench 用成对盲评来衡量它，包括与《风来之国》真实精灵图对照。",
    stCaption: "字符矩阵路线：一份调色板，每个像素一个字符，原样渲染。",
    showTitle: "16×16，直接写成文本", showLead: "同样 12 道题，每个模型各画两次：用技能和不用技能。用技能时，agent 写出网格、渲染、在 1× 下修改看不清的地方。全部使用 extra-high effort。",
    noSkill: "不用技能", judged: "盲评", skillVs: "用技能 vs 不用", bothSkill: "都用技能",
    conceptTitle: "64×64，从 gpt-image 概念图出发", conceptLead: "生图路线：Codex 的 gpt-image 设计角色，转换器还原真正的像素，agent 负责挑选、修改和清理。",
    conceptA: "gpt-image 概念图", conceptB: "真像素",
    reconTitle: "只凭三行描述重画", reconLead: "真实的《风来之国》角色，由从未见过原图的 agent 只凭 3–5 句描述画出，再与原图对照盲评。",
    vsV12: (w, n) => `对 v12：${w}–${n - w}`, setSuite: "测试题", setShowcase: "展示 · 16×16", setConcept: "生图路线 · 64×64",
    ctaBoard: "查看排行榜", ctaSkill: "获取技能",
    stChars: "个角色", stEntries: "个参赛版本", stTasks: "道题", stDrawings: "张图", stJudgings: "次评审",
    original: "原图", redrawn: "重画", heroCaption: (n, e) => `${n}：原图与 ${e} 只凭描述画出的图。`,
    charsTitle: "原图与重画", allChars: "全部角色 →",
    benchTitle: "测试项目", benchLead: "同样的描述、同样的画布、同一个去掉了目标角色的参考素材包，用同一套标准评审。",
    reconName: "复原测试", reconDesc: "凭简短描述重画 10 个真实的《风来之国》角色。每组 2 位盲评评审，把作品和原图对照，按 7 项打分。",
    smallName: "小尺寸精灵", smallDesc: "16×16 和 32×32 的图标与角色，没有原图：两张作品并排，按 7 项标准盲评。",
    archiveName: "存档：早期测试题", archiveDesc: "最早几轮（v1–v10）的三道自拟题目：有参考精灵图但没有原图，两两盲评。",
    runs: (n) => `${n} 次评审`, rating: "评分", boardTitle: "排行榜",
    boardNote: "评分：对全部成对评审做 Bradley–Terry 拟合，采用类似 Elo 的尺度，1000 为平均水平。横条是按角色重抽样得到的 90% 区间；区间重叠说明评审目前还分不出高下。",
    thEntry: "版本", thRating: "评分（90% 区间）", thVs: "对 v12", thMean: "平均 /70", thCalls: "调用", thOut: "输出", thMin: "分钟", thDrawn: "图数",
    histTitle: "各版本的评分", histNote: "按版本编写的先后排列。每一版新规则都是针对评审的意见写的，但评分始终落在彼此的区间之内。虚线：同样的模型不用技能。",
    critTitle: "各项得分", critNote: "该版本在所有评审中的平均分（满分 10）。各版本的对手不同，看整行，不要看细微差距。",
    costNote: "成本是每张图的中位数：API 调用次数、输出 token、实际用时（已扣除中断）。生图路线另外调用了外部图像模型，未计入。",
    charsLead: "每个角色只凭描述来画。“保留角色”是在被测版本写完之后才选出的。",
    heldout: "保留", brief: "描述", attemptsTitle: "全部作品", best: "最佳", won: "胜", notes: "评审认为还欠缺的地方",
    noJudging: "未评审", cost: (c) => `${c.calls} 次调用 · 输出 ${Math.round(c.out / 1000)}k · ${Math.round(c.minutes)} 分钟`,
    smallLead: "16×16 和 32×32 的固定题目，没有原图可照。每对作品由 2 位评审盲评（左右互换），评可读性、轮廓、体积、配色、干净程度、切题和吸引力。",
    smallPairs: "两两对比", smallTasks: "全部题目", pending: "等待结果",
    archiveLead: "最早几轮用的是自拟题目、没有原图：两个版本并排，评审参照风格参考图打分。v1、v3 早于评审流程，v10 在评审前被叫停。",
    methodTitle: "方法", skillTitle: "pixel-art 技能", copy: "复制", copied: "已复制",
    installNote: "支持 Claude Code、Codex、Cursor 等 agent。技能需要装有 pillow、numpy、scipy 的 Python。",
    skillLead: "一个 Claude Code 技能，能画出任意尺寸、真正逐像素的 PNG 像素图。它按画布大小选择路线：构建路线的成绩在排行榜上，字符矩阵路线的成绩在小尺寸测试里。",
    routes: "三条路线", install: "安装", use: "使用", results: "测试成绩",
    download: "下载 zip", github: "GitHub",
    footA: "浏览", footB: "关于", footNote: "代码采用 MIT 许可证。《风来之国》© Pixpil，原图经许可展示。字体：Press Start 2P、Pixelify Sans、Fusion Pixel（SIL OFL）。",
    vsAnchor: (w, n) => `${w}–${n - w}`, of70: "/70", judgedBy: (n) => `${n} 次评审`,
  },
};
let lang = html.lang === "zh" ? "zh" : "en";
const t = (k, ...a) => { const v = S[lang][k] ?? S.en[k]; return typeof v === "function" ? v(...a) : v; };
const L = (o) => (o && typeof o === "object" ? o[lang] ?? o.en : o);

const NAMES = {
  apple: ["Apple", "苹果"], key: ["Key", "钥匙"], heart: ["Heart", "心"], gem: ["Gem", "宝石"], lantern: ["Lantern", "油灯"],
  spellbook: ["Spellbook", "魔法书"], bomb: ["Bomb", "炸弹"], ghost: ["Ghost", "幽灵"], frog: ["Frog", "青蛙"],
  campfire: ["Campfire", "篝火"], witch: ["Witch", "女巫"], robot: ["Robot", "机器人"], noodle: ["Noodle vendor", "面摊老板"],
  mechanic: ["Mechanic", "机械师"], fisherman: ["Old fisherman", "老渔夫"], fox: ["Fox ranger", "狐狸游侠"],
};
const taskName = (id) => (NAMES[id] ? NAMES[id][lang === "zh" ? 1 : 0] : id);
// Reconstruction entries by model and skill (true = pixel-art 1.0, false = the no-skill baseline).
const RECON = { opus: { name: "Opus 5.5", true: "v8R", false: "opusraw" }, astra: { name: "GPT-6 Astra", true: "astra", false: "astraraw" } };
// 16×16 showcase rows: model, skill entry, no-skill entry.
const SHEET = [["Opus 5.5", "opusx", "base"], ["GPT-6 Astra", "astra", "astraraw"]];
let reconModel = "opus", reconSkill = true, heroTimer = null;

// ---------- helpers ----------
const entryLabel = (e) => (D.entries[e] ? D.entries[e].label.replace("no skill", t("noSkill")) : D.sizeEntries[e] ? L(D.sizeEntries[e].label) : e);
const entryNote = (e) => (D.entries[e] ? L(D.entries[e].note) : "");
const task = (id) => D.recon.tasks.find((x) => x.id === id);
const mean = (xs) => xs.reduce((a, b) => a + b, 0) / xs.length;
const avgTotal = (a) => (a.judgings.length ? mean(a.judgings.map((j) => j.total)) : null);
const winsOf = (a) => a.judgings.filter((j) => j.won).length;
const fmtK = (n) => (n == null ? "—" : n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : `${Math.round(n / 1e3)}k`);

function spr(s, px = 220, alt = "") {
  // integer scale so the sprite is about px tall (never below 1×)
  const k = Math.max(1, Math.floor(px / Math.max(s.h, s.w * 0.8)));
  return `<img class="spr" src="${s.img}" width="${s.w * k}" height="${s.h * k}" alt="${esc(alt)}">`;
}
function seg(frac, n = 10) {
  const on = Math.round(Math.max(0, Math.min(1, frac)) * n);
  return `<span class="seg" aria-hidden="true">${Array.from({ length: n }, (_, i) => `<i class="${i < on ? "on" : ""}"></i>`).join("")}</span>`;
}
const rankBadge = (i) => `<span class="rank ${i < 3 ? "r" + (i + 1) : ""}">${i + 1}</span>`;

// ---------- pages ----------
function home() {
  const R = D.recon;
  const drawings = R.attempts.length + D.small.attempts.length + D.early.attempts.length;
  const judgings = R.judgings + D.small.attempts.reduce((n, a) => n + a.judgings.length, 0) / 2;
  const board = R.leaderboard.slice(0, 5);
  const top = Math.max(...R.leaderboard.map((r) => r.rating));
  const lo = Math.min(...R.leaderboard.map((r) => r.rating));
  return `
  <section class="hero">
    <div>
      <p class="eyebrow">${t("eyebrowHome")}</p>
      <h1>${t("heroA")}<span class="holo">${t("heroB")}</span>${t("heroC")}</h1>
      <p class="lead">${t("heroLead")}</p>
      ${installBox()}
      <div class="ctas"><a class="btn primary" href="#/leaderboard">${t("ctaBoard")}</a><a class="btn" href="#/skill">${t("ctaSkill")}</a></div>
      <div class="stats">
        <div><b>${R.tasks.length + D.small.tasks.length}</b><span>${t("stTasks")}</span></div>
        <div><b>${drawings}</b><span>${t("stDrawings")}</span></div>
        <div><b>${Math.round(judgings)}</b><span>${t("stJudgings")}</span></div>
      </div>
    </div>
    <div>${spriteTextWindow()}</div>
  </section>
  ${showcase()}
  ${conceptSection()}
  <section id="recon">${reconSection()}</section>
  <section>
    <h2>${t("benchTitle")}</h2><p class="note">${t("benchLead")}</p>
    <div class="bench">
      <a class="frame card" href="#/leaderboard">
        <h3>${t("reconName")}</h3><p class="muted small">${t("reconDesc")}</p>
        <p class="tiny faint">${t("runs", R.judgings)}</p>
        <ol class="mini">${board.map((r, i) => `<li><span class="n">${i + 1}</span><span>${esc(entryLabel(r.entry))}</span><span class="v">${r.rating}</span>${seg((r.rating - lo + 20) / (top - lo + 20))}</li>`).join("")}</ol>
      </a>
      <a class="frame card" href="#/small">
        <h3>${t("smallName")}</h3><p class="muted small">${t("smallDesc")}</p>
        ${D.small.pairings.length ? `<ol class="mini">${sortedPairings().map((p) => pairingLine(p)).join("")}</ol>` : `<p class="faint small">${t("pending")}</p>`}
      </a>
    </div>
  </section>`;
}

// Hero window: a showcase sprite as the text the model wrote (each key in its palette color) beside the rendered
// pixels. Rows type in while the sprite reveals in step; startHero() cycles through the showcase.
const heroItems = () => D.small.attempts.filter((a) => a.entry === "opusx" && a.grid);
function spriteTextWindow() {
  const items = heroItems();
  if (!items.length) return "";
  return `<div class="frame window st" id="st">${stFrame(items[0])}</div><p class="caption">${t("stCaption")}</p>`;
}
function stFrame(a) {
  const g = a.grid;
  const rows = g.rows.map((r, i) => `<div style="animation-delay:${i * 50}ms">${[...r].map((c) => (c === "." ? "<i>.</i>" : `<b style="color:${g.palette[c]}">${esc(c)}</b>`)).join("")}</div>`).join("");
  const pal = Object.entries(g.palette).map(([k, hex]) => `<span><i style="background:${hex}"></i>${esc(k)}</span>`).join("");
  return `<div class="bar"><i style="background:#ff004d"></i><i style="background:#ffec27"></i><i style="background:#00e436"></i><span>${esc(a.task)}.txt → ${esc(a.task)}.png</span></div>
    <div class="st-body" style="--rows:${g.rows.length}">
      <div><div class="st-grid">${rows}</div><div class="st-pal">${pal}</div></div>
      <div class="st-out"><img class="spr" src="${a.img}" width="${a.w * 13}" height="${a.h * 13}" alt="${esc(taskName(a.task))}"><span>${esc(taskName(a.task))} · ${a.w}×${a.h}</span></div>
    </div>`;
}
function startHero() {
  clearInterval(heroTimer);
  const items = heroItems(), el = $("#st");
  if (!el || items.length < 2 || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  let i = 0;
  heroTimer = setInterval(() => {
    i = (i + 1) % items.length;
    el.classList.add("fade");
    setTimeout(() => { el.innerHTML = stFrame(items[i]); el.classList.remove("fade"); }, 250);
  }, 4200);
}

const toggle = (name, options, current) => `<div class="toggle">${Object.entries(options).map(([k, label]) =>
  `<button data-${name}="${k}" class="${k === current ? "on" : ""}" aria-pressed="${k === current}">${esc(label)}</button>`).join("")}</div>`;

// 16×16 showcase as a sprite sheet: per model a row with the skill and one without, a column per brief.
function showcase() {
  const tasks = D.small.tasks.filter((x) => x.set === "showcase");
  const has = (e) => D.small.attempts.some((a) => a.entry === e && tasks.some((x) => x.id === a.task));
  const rows = SHEET.flatMap(([name, skill, plain]) => [[name, skill, true], [name, plain, false]]).filter(([, e]) => has(e));
  if (!tasks.length || !rows.length) return "";
  const cell = (x, e) => {
    const a = D.small.attempts.find((q) => q.task === x.id && q.entry === e);
    return `<div class="cell" data-tip="${esc(L(x.brief))}">${a ? `<img class="spr" src="${a.img}" width="${a.w * 5}" height="${a.h * 5}" alt="${esc(taskName(x.id))}">` : ""}</div>`;
  };
  // a's and b's wins over the showcase briefs only (the size pairings also count other 16×16 tasks)
  const score = (a, b) => {
    const won = (e, o) => D.small.attempts.filter((q) => q.entry === e && tasks.some((x) => x.id === q.task))
      .flatMap((q) => q.judgings).filter((j) => j.opp === o && j.won).length;
    const [wa, wb] = [won(a, b), won(b, a)];
    return wa + wb ? `${wa}–${wb}` : null;
  };
  const vs = SHEET.map(([name, skill, plain]) => [name, score(skill, plain)]).filter(([, s]) => s);
  const cross = score("opusx", "astra");
  const line = [vs.length ? `${t("skillVs")}: ${vs.map(([n, s]) => `${n} <b>${s}</b>`).join(" · ")}` : "",
    cross ? `Opus 5.5 vs GPT-6 Astra (${t("bothSkill")}): <b>${cross}</b>` : ""].filter(Boolean).join(" · ");
  return `<section><p class="eyebrow">Grid route · 16×16</p><h2>${t("showTitle")}</h2><p class="note">${t("showLead")}</p>
    <div class="frame sheet-wrap"><div class="sheet" style="--cols:${tasks.length}">
      ${tasks.map((x) => `<span class="col">${esc(taskName(x.id))}</span>`).join("")}
      ${rows.map(([name, e, skill]) => `<span class="row ${skill ? "" : "plain"}">${esc(name)} · ${skill ? "pixel-art" : esc(t("noSkill"))}</span>${tasks.map((x) => cell(x, e)).join("")}`).join("")}
    </div></div>
    ${line ? `<p class="small muted" style="margin-top:12px">${t("judged")} · ${line}</p>` : ""}</section>`;
}

function conceptSection() {
  const items = D.small.tasks.filter((x) => x.set === "concept")
    .map((x) => [x, D.small.attempts.find((a) => a.task === x.id && a.entry === "concept")]).filter(([, a]) => a && a.concept);
  if (!items.length) return "";
  return `<section><p class="eyebrow">Concept route · gpt-image</p><h2>${t("conceptTitle")}</h2><p class="note">${t("conceptLead")}</p>
    <div class="concepts">${items.map(([x, a]) => `<figure class="frame concept" data-tip="${esc(L(x.brief))}">
      <div class="concept-pair">
        <div class="concept-img"><img src="${a.concept}" alt="${esc(t("conceptA"))}" loading="lazy"></div>
        <div class="stage concept-px"><img class="spr" src="${a.img}" width="${a.w * 4}" height="${a.h * 4}" alt="${esc(taskName(x.id))}"></div>
      </div>
      <figcaption><b>${esc(taskName(x.id))}</b><span>${t("conceptA")} → ${t("conceptB")} · ${a.w}×${a.h}</span></figcaption></figure>`).join("")}</div></section>`;
}

function reconSection() {
  const R = D.recon;
  const judged = (e) => R.attempts.some((a) => a.entry === e && a.judgings.length);
  const models = Object.keys(RECON).filter((m) => judged(RECON[m].true));
  const entry = RECON[reconModel][reconSkill];
  const row = R.leaderboard.find((r) => r.entry === entry);
  const controls = [models.length > 1 ? toggle("rmodel", Object.fromEntries(models.map((m) => [m, RECON[m].name])), reconModel) : "",
    judged(RECON[reconModel].false) ? toggle("rskill", { true: "pixel-art", false: t("noSkill") }, String(reconSkill)) : ""].join("");
  return `<div class="section-head"><div><p class="eyebrow">Construct route · Eastward</p><h2>${t("reconTitle")}</h2><p class="note">${t("reconLead")}</p></div>
    <div class="controls">${controls}</div></div>
    <div class="cards">${R.tasks.map((x) => charCard(x, entry)).join("")}</div>
    <p class="tiny faint" style="margin-top:14px">${row && row.vsAnchor.n ? `${esc(entryLabel(entry))} ${t("vsV12", row.vsAnchor.w, row.vsAnchor.n)} · ${t("rating")} ${row.rating} · ` : ""}<a href="#/leaderboard">${t("ctaBoard")} →</a></p>`;
}

// Original beside one drawing: the requested entry's if it has one, else the release's, else the best judged.
function charCard(x, entry) {
  const R = D.recon;
  const atts = R.attempts.filter((a) => a.task === x.id && a.judgings.length);
  const shown = atts.find((a) => a.entry === entry) || atts.find((a) => D.entries[a.entry]?.release)
    || atts.sort((a, b) => avgTotal(b) - avgTotal(a))[0];
  return `<a class="frame card" href="#/characters/${x.id}">
    <div class="title">${esc(x.name)} ${x.heldout ? `<span class="tag alt">${t("heldout")}</span>` : ""}</div>
    <div class="pair" style="margin:10px">
      <div class="stage sand" style="height:150px;border:2px solid var(--border)">${spr(x.original, 128, x.name)}</div>
      <div class="stage sand" style="height:150px;border:2px solid var(--border);border-left:0">${shown ? spr(shown, 128, entryLabel(shown.entry)) : ""}</div>
    </div>
    <div class="meta">${t("original")} · ${shown ? `${esc(entryLabel(shown.entry))} · ${avgTotal(shown).toFixed(0)}${t("of70")}` : ""}</div>
  </a>`;
}

// Head-to-head line: the skill's entry first, the leader in bold, the bar showing the leader's share.
const PAIR_ORDER = ["lite", "grid", "cons", "opusx", "astra", "concept", "base", "astraraw"];
function pairingLine(p) {
  const [a, b] = [...p.entries].sort((x, y) => PAIR_ORDER.indexOf(x) - PAIR_ORDER.indexOf(y));
  const wa = p.wins[a] || 0, wb = p.wins[b] || 0;
  const name = (e, w, o) => (w > o ? `<b>${esc(entryLabel(e))}</b>` : `<span class="muted">${esc(entryLabel(e))}</span>`);
  return `<li><span class="n">${p.size}</span><span>${name(a, wa, wb)} <span class="faint">vs</span> ${name(b, wb, wa)}</span><span class="v">${wa}–${wb}</span>${seg(Math.max(wa, wb) / p.n)}</li>`;
}
const sortedPairings = () => [...D.small.pairings].sort((p, q) => p.size - q.size
  || PAIR_ORDER.indexOf(p.entries.find((e) => e !== "base") || "base") - PAIR_ORDER.indexOf(q.entries.find((e) => e !== "base") || "base"));

function leaderboardPage() {
  const R = D.recon;
  const rows = R.leaderboard;
  const lo = Math.min(...rows.map((r) => r.lo)) - 20, hi = Math.max(...rows.map((r) => r.hi)) + 20;
  const ci = (r) => {
    const W = 220, x = (v) => ((v - lo) / (hi - lo)) * W;
    return `<svg class="chart" viewBox="0 0 ${W} 22" width="${W}" height="22" data-tip="${esc(`${entryLabel(r.entry)}: ${r.rating} (${r.lo}–${r.hi})`)}">
      <line class="grid" x1="${x(1000)}" x2="${x(1000)}" y1="0" y2="22"/>
      <rect x="${x(r.lo)}" y="9" width="${Math.max(2, x(r.hi) - x(r.lo))}" height="4" fill="var(--frame)"/>
      <rect x="${x(r.rating) - 5}" y="6" width="10" height="10" fill="${D.entries[r.entry]?.release ? "var(--accent)" : "var(--sky)"}"/></svg>`;
  };
  return `
  <section style="margin-top:56px">
    <p class="eyebrow">${t("navBoard")}</p><h1>${t("boardTitle")}</h1>
    <p class="note">${t("boardNote")}</p>
    <div class="frame lbwrap"><table class="lb">
      <thead><tr><th>#</th><th>${t("thEntry")}</th><th>${t("thRating")}</th><th>${t("thVs")}</th><th>${t("thMean")}</th><th>${t("thCalls")}</th><th>${t("thOut")}</th><th>${t("thMin")}</th><th>${t("thDrawn")}</th></tr></thead>
      <tbody>${rows.map((r, i) => `<tr class="${D.entries[r.entry]?.release ? "release" : ""}">
        <td>${rankBadge(i)}</td>
        <td><div class="name">${esc(entryLabel(r.entry))}</div><div class="sub">${esc(entryNote(r.entry))}</div></td>
        <td><span class="num" style="font:13px 'Press Start 2P',monospace">${r.rating}</span><br>${ci(r)}</td>
        <td class="num">${r.entry === R.anchor ? "—" : r.vsAnchor.n ? t("vsAnchor", r.vsAnchor.w, r.vsAnchor.n) : "—"}</td>
        <td class="num">${r.mean.toFixed(1)}</td>
        <td class="num">${r.calls == null ? "—" : Math.round(r.calls)}</td><td class="num">${fmtK(r.out)}</td><td class="num">${r.minutes == null ? "—" : Math.round(r.minutes)}</td>
        <td class="num">${r.drawn}</td></tr>`).join("")}</tbody></table></div>
    <p class="note">${t("costNote")}</p>
  </section>
  <section><h2>${t("histTitle")}</h2><p class="note">${t("histNote")}</p><div class="frame chartbox">${historyChart(rows)}</div></section>
  <section><h2>${t("critTitle")}</h2><p class="note">${t("critNote")}</p><div class="frame chartbox" style="overflow-x:auto">${critHeat(rows)}</div></section>`;
}

function historyChart(rows) {
  const order = Object.keys(D.entries).filter((e) => !D.entries[e].baseline && rows.some((r) => r.entry === e));
  const base = rows.filter((r) => D.entries[r.entry]?.baseline).sort((p, q) => q.rating - p.rating);
  const by = Object.fromEntries(rows.map((r) => [r.entry, r]));
  const W = 960, H = 300, ml = 48, mb = 40, mt = 14;
  const lo = Math.floor((Math.min(...rows.map((r) => r.lo)) - 20) / 50) * 50, hi = Math.ceil((Math.max(...rows.map((r) => r.hi)) + 20) / 50) * 50;
  const y = (v) => mt + (H - mt - mb) * (1 - (v - lo) / (hi - lo));
  const x = (i) => ml + ((W - ml - 20) * (i + 0.5)) / order.length;
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(t("histTitle"))}">`;
  for (let v = lo; v <= hi; v += 50) s += `<line class="grid" x1="${ml}" x2="${W - 20}" y1="${y(v)}" y2="${y(v)}"/><text x="${ml - 8}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
  s += `<line class="axis" x1="${ml}" x2="${W - 20}" y1="${H - mb}" y2="${H - mb}"/>`;
  base.forEach((r, i) => {
    s += `<g data-tip="${esc(`${entryLabel(r.entry)} · ${r.rating} (90 %: ${r.lo}–${r.hi}) · ${r.wins}/${r.games}`)}">
      <line x1="${ml}" x2="${W - 20}" y1="${y(r.rating)}" y2="${y(r.rating)}" stroke="var(--bad)" stroke-width="2" stroke-dasharray="6 6"/>
      <text x="${W - 22}" y="${y(r.rating) + (i % 2 ? 16 : -6)}" text-anchor="end" fill="var(--bad)">${esc(entryLabel(r.entry))}</text></g>`;
  });
  order.forEach((e, i) => {
    const r = by[e], rel = D.entries[e]?.release, c = rel ? "var(--accent)" : "var(--sky)";
    s += `<g data-tip="${esc(`${entryLabel(e)} · ${r.rating} (90 %: ${r.lo}–${r.hi}) · ${r.wins}/${r.games}`)}">
      <rect x="${x(i) - 24}" y="${mt}" width="48" height="${H - mt - mb}" fill="transparent"/>
      <line x1="${x(i)}" x2="${x(i)}" y1="${y(r.lo)}" y2="${y(r.hi)}" stroke="var(--frame)" stroke-width="4"/>
      <rect x="${x(i) - 7}" y="${y(r.rating) - 7}" width="14" height="14" fill="${c}"/>
      <text class="lbl" x="${x(i)}" y="${H - mb + 20}" text-anchor="middle">${esc(rel ? (e === "astra" ? "1.0 Astra" : "1.0 Opus") : e)}</text></g>`;
  });
  return s + "</svg>";
}

function ramp(v, vmin, vmax) {
  // sequential: one hue, dark (low) to light (high) on the dark theme
  const f = Math.max(0, Math.min(1, (v - vmin) / (vmax - vmin)));
  const a = [0x3a, 0x2a, 0x10], b = [0xff, 0xc8, 0x5c];
  const c = a.map((x, i) => Math.round(x + (b[i] - x) * f));
  return { bg: `rgb(${c.join(",")})`, ink: f > 0.55 ? "#1b1824" : "#f1edf6" };
}

function critHeat(rows) {
  const C = D.recon.criteria;
  const names = { en: ["proportions", "volume", "shapes", "shading", "face", "palette", "craft"], zh: ["比例", "体积感", "形状", "明暗", "脸部", "配色", "完成度"] };
  return `<table class="heat"><tr><th></th>${C.map((c, i) => `<th>${names[lang][i]}</th>`).join("")}</tr>${rows.map((r) => `<tr><th class="row">${esc(entryLabel(r.entry))}</th>${C.map((c) => {
    const v = r.criteria[c], k = ramp(v, 4.2, 6.2);
    return `<td style="background:${k.bg};color:${k.ink}" data-tip="${esc(`${entryLabel(r.entry)} · ${c}: ${v.toFixed(2)}/10`)}">${v.toFixed(1)}</td>`;
  }).join("")}</tr>`).join("")}</table>`;
}

function charactersPage() {
  return `<section style="margin-top:56px"><p class="eyebrow">${t("reconName")}</p><h1>${t("navChars")}</h1>
    <p class="note">${t("charsLead")}</p><div class="cards">${D.recon.tasks.map((x) => charCard(x)).join("")}</div></section>`;
}

function characterPage(id) {
  const x = task(id);
  if (!x) return notFound();
  const atts = D.recon.attempts.filter((a) => a.task === id).sort((a, b) => (avgTotal(b) ?? -1) - (avgTotal(a) ?? -1));
  return `<section class="task-head">
    <div class="frame"><div class="stage sand" style="padding:28px 36px">${spr(x.original, 320, x.name)}</div></div>
    <div><p class="eyebrow">${t("reconName")} · ${x.canvas[0]}×${x.canvas[1]}</p><h1>${esc(x.name)}</h1>
      ${x.heldout ? `<p><span class="tag alt">${t("heldout")}</span></p>` : ""}
      <p class="brief">${esc(L(x.brief))}</p>
      <p class="tiny faint">${x.original.w}×${x.original.h} px · ${x.original.colors} colors</p></div>
  </section>
  <section><h2>${t("attemptsTitle")}</h2><div class="attempts">${atts.map((a, i) => attemptCard(a, i === 0)).join("")}</div></section>`;
}

function attemptCard(a, isBest) {
  const tot = avgTotal(a), w = winsOf(a), n = a.judgings.length;
  const notes = [...new Set(a.judgings.flatMap((j) => j.notes))];
  const vs = [...new Set(a.judgings.map((j) => j.opp))].map(entryLabel).join(", ");
  return `<div class="frame card attempt">
    <div class="title">${esc(entryLabel(a.entry))} ${isBest ? `<span class="tag">${t("best")}</span>` : ""}${D.entries[a.entry]?.release ? `<span class="tag alt">1.0</span>` : ""}</div>
    <div class="stage sand" style="height:230px">${spr(a, 200, entryLabel(a.entry))}</div>
    <div class="scorebar">${tot == null ? `<span class="faint">${t("noJudging")}</span>` : `<span class="num" style="font:12px 'Press Start 2P',monospace">${tot.toFixed(0)}${t("of70")}</span><span class="${w * 2 >= n ? "win" : "loss"}">${t("won")} ${w}/${n}</span>`}</div>
    <div class="meta">${vs ? `vs ${esc(vs)}` : ""}${a.cost ? `<br>${t("cost", a.cost)}` : ""}</div>
    ${notes.length ? `<details><summary>${t("notes")}</summary><ul>${notes.slice(0, 6).map((s) => `<li>${esc(s)}</li>`).join("")}</ul></details>` : ""}
  </div>`;
}

function smallPage() {
  const Sm = D.small;
  const table = ([set, title]) => {
    const tasks = Sm.tasks.filter((x) => x.set === set);
    const entries = Object.keys(D.sizeEntries).filter((e) => Sm.attempts.some((a) => a.entry === e && tasks.some((x) => x.id === a.task)));
    if (!tasks.length || !entries.length) return "";
    const rows = tasks.map((x) => {
      const k = x.canvas[0] > 32 ? 3 : 6;
      const cells = entries.map((e) => {
        const a = Sm.attempts.find((q) => q.task === x.id && q.entry === e);
        if (!a) return `<td></td>`;
        const w = winsOf(a), n = a.judgings.length;
        return `<td><div class="stage" style="width:${x.canvas[0] * k + 24}px;height:${x.canvas[1] * k + 32}px;border:2px solid var(--border)"><img class="spr" src="${a.img}" width="${a.w * k}" height="${a.h * k}" alt=""></div>
          <div class="tiny ${n ? (w * 2 >= n ? "win" : "loss") : "faint"}">${n ? `${t("won")} ${w}/${n}` : t("noJudging")}</div></td>`;
      }).join("");
      return `<tr><td style="min-width:220px;max-width:300px"><div style="font:10px/1.6 'Press Start 2P',monospace">${x.canvas[0]}×${x.canvas[1]}</div><div class="small muted">${esc(L(x.brief))}</div></td>${cells}</tr>`;
    }).join("");
    return `<h3 class="display" style="font-size:13px;margin:32px 0 12px">${esc(title)}</h3><div class="frame" style="overflow-x:auto;padding:12px">
      <table class="small-grid"><tr><th></th>${entries.map((e) => `<th>${esc(entryLabel(e))}</th>`).join("")}</tr>${rows}</table></div>`;
  };
  return `<section style="margin-top:56px"><p class="eyebrow">${t("smallName")}</p><h1>${t("navSmall")}</h1><p class="note">${t("smallLead")}</p>
    ${Sm.pairings.length ? `<div class="frame" style="padding:20px 24px;max-width:860px"><h3 class="display" style="font-size:13px">${t("smallPairs")}</h3><ol class="mini">${sortedPairings().map((p) => pairingLine(p)).join("")}</ol></div>` : `<p class="faint">${t("pending")}</p>`}
  </section>
  <section><h2>${t("smallTasks")}</h2>${[["suite", t("setSuite")], ["showcase", t("setShowcase")], ["concept", t("setConcept")]].map(table).join("")}</section>`;
}

function archivePage() {
  const E = D.early;
  const head = `<tr><th></th>${E.tasks.map((x) => `<th>${esc(L(x.name))}</th>`).join("")}</tr>`;
  const rows = E.versions.map((v) => `<tr><td><div class="name" style="font:11px 'Press Start 2P',monospace">${v}</div><div class="tiny muted">${esc(L(E.notes[v]) || "")}</div></td>${E.tasks.map((x) => {
    const a = E.attempts.find((q) => q.entry === v && q.task === x.id);
    if (!a) return `<td class="faint">—</td>`;
    return `<td><div class="stage sand" style="height:${Math.max(a.h * 3 + 24, 120)}px;border:2px solid var(--border)">${`<img class="spr" src="${a.img}" width="${a.w * 3}" height="${a.h * 3}" alt="">`}</div>
      <div class="tiny ${a.games ? (a.wins * 2 >= a.games ? "win" : "loss") : "faint"}">${a.games ? `${t("won")} ${a.wins}/${a.games} · ${a.mean}/80` : t("noJudging")}</div></td>`;
  }).join("")}</tr>`).join("");
  return `<section style="margin-top:56px"><p class="eyebrow">${t("archiveName")}</p><h1>${t("archiveName")}</h1><p class="note">${t("archiveLead")}</p>
    <div class="frame" style="overflow-x:auto;padding:12px"><table class="small-grid">${head}${rows}</table></div></section>`;
}

const METHOD = {
  en: `
  <h2>Protocol</h2><ol class="steps">
    <li><b>Targets.</b> 10 real Eastward characters (48×64 adults, 32×48 kids), 4 of them held out: chosen after the skill version under test was written.</li>
    <li><b>Brief.</b> Each target is described in 3–5 sentences: build, hair, face, clothes, props, pose. Nothing else about it is given.</li>
    <li><b>Drawer.</b> A fresh agent (Claude Opus 5.5) with only the skill under test, the brief, Python, and the game's sprite pack with every target removed. It never sees the original. The skill copy is scrubbed of the target's name.</li>
    <li><b>Pairing.</b> Two attempts at the same character are shown next to the original (8× and game size), anonymized as X and Y. Two judges see the pair, the second with X and Y swapped. The key stays outside the packet.</li>
    <li><b>Judging.</b> Each judge (a fresh Claude agent with vision) scores both attempts 1–10 on 7 criteria against the original, picks the closer one, and names the 3 biggest things the better one still misses.</li>
    <li><b>Rating.</b> A Bradley–Terry fit over every judging, shown on an Elo-like scale (1000 = average entry), with a 90 % interval from resampling whole characters.</li></ol>
  <h2>Rubric</h2><ul class="plain">
    <li><b>proportions</b> — head, body and limb sizes; height and width; how the figure tapers</li>
    <li><b>volume</b> — reads as seen slightly from above like the original, not flat, front-on or cylindrical</li>
    <li><b>shapes</b> — shape language of hair, clothes, hands and feet</li>
    <li><b>shading</b> — where shadows and highlights sit, number of tones, cleanliness</li>
    <li><b>face</b> — construction and expression</li>
    <li><b>palette</b> — colors and value range</li>
    <li><b>craft</b> — quality as game pixel art</li></ul>
  <h2>Read with care</h2><ul class="plain">
    <li><b>One drawing per entry per character.</b> A single drawing can be lucky. The intervals carry that uncertainty; most of them overlap.</li>
    <li><b>The character decides more than the version.</b> v12's drawing won 15 of 16 judgings on some characters and 1 of 16 on others. Later versions were judged against those same v12 drawings, so a version's total partly reflects which v12 drawings it met.</li>
    <li><b>Judges are models.</b> They are consistent and blind, but they are not players. Their notes are shown so you can disagree.</li>
    <li><b>Cost</b> is per drawing: API calls, output tokens and active minutes (interruptions subtracted). Runs in parallel with 10–20 other agents were slower per request.</li></ul>`,
  zh: `
  <h2>流程</h2><ol class="steps">
    <li><b>目标。</b>10 个真实的《风来之国》角色（成人 48×64，儿童 32×48），其中 4 个是保留角色：在被测版本写完之后才选出。</li>
    <li><b>描述。</b>每个角色用 3–5 句话描述：体型、头发、脸、衣服、道具、姿势，除此之外不给任何信息。</li>
    <li><b>画图。</b>一个全新的 agent（Claude Opus 5.5），只有被测技能、描述、Python，以及去掉了所有目标角色的游戏精灵素材包。它从未见过原图；技能副本里也删掉了目标角色的名字。</li>
    <li><b>配对。</b>同一角色的两张作品匿名为 X、Y，放在原图旁（8× 和游戏尺寸）。两位评审看同一对，第二位的 X、Y 左右互换；对应关系存放在评审看不到的地方。</li>
    <li><b>评审。</b>每位评审（一个全新的、能看图的 Claude agent）对照原图给两张作品的 7 项各打 1–10 分，选出更接近原图的一张，并指出它最欠缺的 3 点。</li>
    <li><b>评分。</b>对全部评审做 Bradley–Terry 拟合，用类似 Elo 的尺度表示（1000 = 平均水平），并按角色重抽样给出 90% 区间。</li></ol>
  <h2>评分项</h2><ul class="plain">
    <li><b>比例</b>：头、身体、四肢的大小；高度和宽度；整体如何收窄</li>
    <li><b>体积感</b>：像原图一样略带俯视，而不是扁平、正面或圆柱状</li>
    <li><b>形状</b>：头发、衣服、手脚的造型语言</li>
    <li><b>明暗</b>：阴影和高光的位置、色阶数量、是否干净</li>
    <li><b>脸部</b>：结构和表情</li>
    <li><b>配色</b>：颜色选择和明度范围</li>
    <li><b>完成度</b>：作为游戏像素图的整体质量</li></ul>
  <h2>解读时请注意</h2><ul class="plain">
    <li><b>每个版本每个角色只有一张图。</b>单张图可能是运气好。区间已经包含了这部分不确定性，大部分区间是重叠的。</li>
    <li><b>角色本身比版本影响更大。</b>v12 的图在有的角色上赢了 16 次中的 15 次，在有的角色上只赢 1 次。后来的版本都是和这同一批 v12 的图比的，所以总分部分取决于碰上了哪几张 v12 图。</li>
    <li><b>评审是模型。</b>它们一致且盲评，但不是玩家。评审意见都附在作品旁，欢迎不同意。</li>
    <li><b>成本</b>按每张图计：API 调用、输出 token、实际用时（已扣除中断）。和 10–20 个 agent 并行的运行，单次请求更慢。</li></ul>`,
};

function methodPage() {
  return `<section style="margin-top:56px"><p class="eyebrow">${t("navMethod")}</p><h1>${t("methodTitle")}</h1><div class="frame" style="padding:8px 28px 20px;max-width:900px">${METHOD[lang]}</div></section>`;
}

const SKILL = {
  en: {
    routes: [
      ["up to 32 px", "Grid", "Writes the palette and the pixel grid directly as text, renders it, checks it at 1× and fixes it. Icons, items, tiles and small characters."],
      ["over 32 px", "Construct", "Code builds the figure and its light from polygons; the agent draws faces, hands and details at full size in ≤ 16×16 windows, seen from slightly above. Benchmarked here."],
      ["32 px and up, optional", "Concept", "With Codex image generation (gpt-image): an image model designs the sprite, a converter recovers the true pixels, the agent fixes only conversion artifacts."],
    ],
    install: `npx skills add junyudev/pixel-art        # this project
npx skills add junyudev/pixel-art -g     # every project
pip install pillow numpy scipy`,
    use: ["Draw a 16×16 health potion icon.", "Make a 48×64 front-facing idle sprite of a grumpy fishmonger, Eastward style.", "Turn this concept image into a 64×64 pixel-art sprite."],
    codex: "Optional concept route: install the Codex CLI and log in (codex login); the skill checks codex features list for image_generation and offers it for sprites of 32 px and up.",
  },
  zh: {
    routes: [
      ["32 px 及以下", "字符矩阵", "直接把调色板和像素网格写成文本，渲染后在 1× 下检查、修改。适合图标、物品、地块和小角色。"],
      ["32 px 以上", "构建", "代码用多边形搭出人物和统一光照；agent 在 ≤16×16 的窗口里按原尺寸画脸、手和细节，视角略带俯视。本站测试的就是这条路线。"],
      ["32 px 及以上，可选", "生图", "有 Codex 生图（gpt-image）时：图像模型设计角色，转换器还原真正的像素，agent 只修转换产生的瑕疵。"],
    ],
    install: `npx skills add junyudev/pixel-art        # 当前项目
npx skills add junyudev/pixel-art -g     # 所有项目
pip install pillow numpy scipy`,
    use: ["画一个 16×16 的生命药水图标。", "按《风来之国》的风格，画一个 48×64、正面待机、脾气暴躁的鱼贩。", "把这张概念图转成 64×64 的像素精灵图。"],
    codex: "可选的生图路线：安装 Codex CLI 并登录（codex login）；技能会用 codex features list 检查 image_generation，32 px 及以上的图会提示你可以使用。",
  },
};

function skillPage() {
  const K = SKILL[lang];
  const rel = D.recon.leaderboard.find((r) => D.entries[r.entry]?.release);
  const rank = rel ? D.recon.leaderboard.indexOf(rel) + 1 : null;
  return `<section style="margin-top:56px"><p class="eyebrow">Claude Code skill</p><h1>${t("skillTitle")}</h1><p class="lead">${t("skillLead")}</p>
    ${installBox()}
    <div class="ctas" style="display:flex;gap:16px;margin:24px 0"><a class="btn primary" href="${REPO}">${t("github")}</a><a class="btn" href="download/pixel-art.zip" download>${t("download")}</a><a class="btn" href="#/leaderboard">${t("ctaBoard")}</a></div></section>
  <section><h2>${t("routes")}</h2><div class="routes">${K.routes.map(([size, name, desc]) => `<div class="frame"><div class="eyebrow" style="margin:0">${esc(name)}</div><div class="size">${esc(size)}</div><p class="muted small">${esc(desc)}</p></div>`).join("")}</div>
    <p class="note">${esc(K.codex)}</p></section>
  <section><h2>${t("install")}</h2><pre>${esc(K.install)}</pre></section>
  <section><h2>${t("use")}</h2><ul class="plain">${K.use.map((u) => `<li>“${esc(u)}”</li>`).join("")}</ul></section>
  ${rel ? `<section><h2>${t("results")}</h2><div class="frame" style="padding:20px 24px;max-width:760px">
    <p><span class="rank ${rank <= 3 ? "r" + rank : ""}">${rank}</span> &nbsp;<b>${esc(entryLabel(rel.entry))}</b> · ${t("rating")} ${rel.rating} (${rel.lo}–${rel.hi}) · ${t("thVs")} ${t("vsAnchor", rel.vsAnchor.w, rel.vsAnchor.n)} · ${rel.mean}${t("of70")}</p>
    ${D.small.pairings.length ? `<ol class="mini">${sortedPairings().map((p) => pairingLine(p)).join("")}</ol>` : ""}</div></section>` : ""}`;
}

function installBox() {
  return `<div class="install"><code><span class="prompt">$</span> ${esc(INSTALL)}</code>
    <button class="copy" data-copy="${esc(INSTALL)}">${t("copy")}</button></div><p class="tiny faint install-note">${t("installNote")}</p>`;
}

function notFound() { return `<section style="margin-top:56px"><h1>404</h1><p><a href="#/">←</a></p></section>`; }

// ---------- shell ----------
const ROUTES = [["#/leaderboard", "navBoard"], ["#/characters", "navChars"], ["#/small", "navSmall"], ["#/method", "navMethod"], ["#/skill", "navSkill"]];

function render() {
  const h = location.hash || "#/";
  const [, page, arg] = h.split("/");
  const view = { "": home, leaderboard: leaderboardPage, characters: () => (arg ? characterPage(arg) : charactersPage()), small: smallPage,
    archive: archivePage, method: methodPage, skill: skillPage }[page || ""] || notFound;
  $("#nav").innerHTML = ROUTES.map(([href, k]) => `<a href="${href}" class="${h.startsWith(href) ? "on" : ""}">${t(k)}</a>`).join("");
  $("#main").innerHTML = view();
  document.querySelectorAll("[data-t]").forEach((el) => (el.textContent = t(el.dataset.t)));
  $("#lang").textContent = lang === "zh" ? "EN" : "中文";
  $("#theme").textContent = html.dataset.theme === "dark" ? "☀" : "☾";
  $("#foot").innerHTML = `<div><h4>${t("footA")}</h4>${ROUTES.map(([href, k]) => `<a href="${href}">${t(k)}</a>`).join("")}<a href="#/archive">${t("archiveName")}</a></div>
    <div style="max-width:520px"><h4>${t("footB")}</h4><a href="${REPO}">github.com/junyudev/pixel-art</a><p>${t("footNote")}</p></div>`;
  if (!arg) window.scrollTo(0, 0);
  clearInterval(heroTimer);
  if (!page) startHero();
}

$("#lang").addEventListener("click", () => { lang = lang === "zh" ? "en" : "zh"; html.lang = lang; localStorage.setItem("lang", lang); render(); });
$("#theme").addEventListener("click", () => { html.dataset.theme = html.dataset.theme === "dark" ? "light" : "dark"; localStorage.setItem("theme", html.dataset.theme); render(); });
window.addEventListener("hashchange", render);
document.addEventListener("click", (e) => {
  const m = e.target.closest("[data-rmodel]"), k = e.target.closest("[data-rskill]");
  if (m) { reconModel = m.dataset.rmodel; $("#recon").innerHTML = reconSection(); return; }
  if (k) { reconSkill = k.dataset.rskill === "true"; $("#recon").innerHTML = reconSection(); return; }
  const b = e.target.closest("[data-copy]");
  if (!b) return;
  navigator.clipboard.writeText(b.dataset.copy).then(() => {
    b.textContent = t("copied");
    setTimeout(() => (b.textContent = t("copy")), 1500);
  });
});
const tip = $("#tip");
document.addEventListener("mousemove", (e) => {
  const el = e.target.closest("[data-tip]");
  if (!el) { tip.style.opacity = 0; return; }
  tip.textContent = el.dataset.tip; tip.style.opacity = 1;
  tip.style.left = Math.min(e.clientX + 14, innerWidth - 380) + "px"; tip.style.top = e.clientY + 16 + "px";
});
render();
