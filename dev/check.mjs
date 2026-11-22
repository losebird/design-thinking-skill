// 开发用：打开 examples/demo 下全部页面，检查控制台报错并截图（桌面 + 手机）。
// 用法（在 /data 下）：node design-thinking-skill/dev/check.mjs [输出目录]
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
const dir = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../examples/demo');
const out = process.argv[2] || '/data/shots'; fs.mkdirSync(out, { recursive: true });
const exe = [process.env.CHROMIUM,'/usr/local/bin/chromium','/usr/bin/chromium'].find(p=>p&&fs.existsSync(p));
const b = await chromium.launch(exe ? { executablePath: exe } : {});
let bad = 0;
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort()) {
  for (const [tag, vp] of [['d', { width: 1280, height: 900 }], ['m', { width: 390, height: 844 }]]) {
    const p = await b.newPage({ viewport: vp });
    const errs = [];
    p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
    await p.goto('file://' + path.join(dir, f)); await p.waitForTimeout(250);
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    await p.screenshot({ path: path.join(out, f.replace('.html', '') + '-' + tag + '.png'), fullPage: true });
    if (errs.length || ov > 2) { bad++; console.log('✗', f, tag, ov > 2 ? '横向溢出 ' + ov + 'px' : '', errs.join(' | ')); }
    await p.close();
  }
}
await b.close(); console.log(bad ? bad + ' 个问题' : '全部通过');
