// 図面の体裁検査(Playwright): 文字同士の重なり、題名欄/改訂欄/図枠への侵入、図枠外へのはみ出しを検出する。
// 使い方: NODE_PATH=$(npm root -g) node tools/drawing_lint.js <svgのパス...>   終了コード: 欠陥があれば 1
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1060 } }); let bad = 0; const out = [];
  for (const f of process.argv.slice(2)) {
    await p.goto('file://' + require('path').resolve(f));
    const r = await p.evaluate(() => {
      const svg = document.querySelector('svg'); const vb = svg.viewBox.baseVal; const W = vb.width, H = vb.height;
      const tb = { x0: W - 10 - 180, y0: H - 10 - 44, x1: W - 10, y1: H - 10 }, rev = { x0: W - 10 - 180 - 100, y0: H - 10 - 44 + 6, x1: W - 10 - 180 - 30, y1: H - 10 - 6 }, sym = { x0: W - 10 - 180 - 30, y0: H - 10 - 44, x1: W - 10 - 180, y1: H - 10 };
      const items = []; for (const t of svg.querySelectorAll('text')) { const bb = t.getBoundingClientRect(); const m = svg.getScreenCTM(); if (!bb.width) continue; const s = 1 / m.a; items.push({ s: t.textContent.trim().slice(0, 40), x0: (bb.left - m.e) * s, y0: (bb.top - m.f) * s, x1: (bb.right - m.e) * s, y1: (bb.bottom - m.f) * s, inTitle: !!t.closest('[data-frame]') }); }
      const hit = (a, r) => a.x0 < r.x1 && r.x0 < a.x1 && a.y0 < r.y1 && r.y0 < a.y1; const issues = [];
      // 題名欄などの枠そのものの文字は frame() 由来(座標がちょうど枠内)。図面本体の文字が枠内に入るものを検出する
      const frameTexts = new Set(items.filter(i => i.inTitle));
      for (const it of items) {
        if (frameTexts.has(it)) continue;
        if (it.x1 > W - 10 || it.x0 < 20 - 1 || it.y1 > H - 10 || it.y0 < 10) issues.push(['図枠外', it.s]);
        else if (hit(it, tb) || hit(it, rev) || hit(it, sym)) issues.push(['題名欄/改訂欄と重なり', it.s]);
      }
      const body = items.filter(i => !frameTexts.has(i) && !hit(i, rev) && !hit(i, sym) && i.y0 > 20 && i.y1 < H - 12);
      for (let i = 0; i < body.length; i++) for (let j = i + 1; j < body.length; j++) { const a = body[i], c = body[j]; const ox = Math.min(a.x1, c.x1) - Math.max(a.x0, c.x0), oy = Math.min(a.y1, c.y1) - Math.max(a.y0, c.y0); if (ox > 1 && oy > 1.2 && ox * oy > 3) issues.push(['文字重なり', a.s + ' × ' + c.s]); }
      return issues;
    });
    const u = [...new Set(r.map(x => x.join(': ')))]; if (u.length) { bad++; out.push('■ ' + f + ' (' + u.length + '件)\n  ' + u.slice(0, 12).join('\n  ')); } else out.push('OK ' + f);
  }
  await b.close(); console.log(out.join('\n')); process.exit(bad ? 1 : 0);
})();
