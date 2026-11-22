// 开发用：打开指定目录下全部 HTML 页面，检查控制台报错并截图（桌面 + 手机）。
// 用法（在 /data 下）：node design-thinking-skill/dev/check.mjs [dir1] [dir2] ... [--out shots目录]
// 若不带参数，检查 examples/demo。
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
const args = process.argv.slice(2);
const outIdx = args.indexOf('--out');
const out = outIdx >= 0 ? args.splice(outIdx, 2)[1] : '/data/shots';
fs.mkdirSync(out, { recursive: true });
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const dirs = args.length ? args.map(a => path.resolve(a)) : [path.join(root, 'examples/demo')];
const exe = [process.env.CHROMIUM,'/usr/local/bin/chromium','/usr/bin/chromium'].find(p=>p&&fs.existsSync(p));
const b = await chromium.launch(exe ? { executablePath: exe } : {});
let bad = 0;
for (const dir of dirs) {
  if (!fs.existsSync(dir)) { console.log('目录不存在，跳过：', dir); continue; }
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort()) {
    for (const [tag, vp] of [['d', { width: 1280, height: 900 }], ['m', { width: 390, height: 844 }]]) {
      const p = await b.newPage({ viewport: vp });
      const errs = [];
      p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
      await p.goto('file://' + path.join(dir, f)); await p.waitForTimeout(250);
      const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      const prefix = path.basename(dir) + '-' + f.replace('.html', '');
      await p.screenshot({ path: path.join(out, prefix + '-' + tag + '.png'), fullPage: true });
      if (errs.length || ov > 2) { bad++; console.log('✗', path.basename(dir)+'/'+f, tag, ov > 2 ? '横向溢出 ' + ov + 'px' : '', errs.join(' | ')); }
      await p.close();
    }
  }
}
await b.close(); console.log(bad ? bad + ' 个问题' : '全部通过'); process.exit(bad ? 1 : 0);
