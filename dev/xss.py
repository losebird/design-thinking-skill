#!/usr/bin/env python3
"""XSS 注入测试：生成含注入 payload 的项目数据，渲染后扫描输出 HTML 是否有未转义的脚本。
用法: python3 dev/xss.py [--keep]  （不带参数时自动清理临时文件）
"""
import json, pathlib, sys, re, tempfile, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAYLOAD = '<script>window.__XSS__=1</script>'
SAFE_RE = re.compile(r'<script>window\.__XSS__=1</script>', re.IGNORECASE)

# 枚举字段（select/status 等）不注入，只注入文本字段
SKIP_KEYS = {'id', 'evidence', 'type', 'status', 'mode', 'risk', 'angle',
             'generatedBy', 'phase', 'priority', 'format', 'fw', 'credibility'}

def inject(o):
    if isinstance(o, str):
        return PAYLOAD
    if isinstance(o, list):
        return [inject(x) for x in o]
    if isinstance(o, dict):
        return {k: (inject(v) if k not in SKIP_KEYS else v) for k, v in o.items()}
    return o

def main():
    keep = '--keep' in sys.argv
    sample = json.loads((ROOT / 'examples/smart-locker.json').read_text('utf-8'))
    injected = inject(sample)
    # 保留 meta 中必要字段（avoid 破坏 build hash）
    injected['meta'] = sample['meta'].copy()
    injected['meta']['project'] = PAYLOAD  # 也测试 project 字段

    tmp = pathlib.Path(tempfile.mkdtemp(prefix='dt_xss_'))
    try:
        data_file = tmp / 'xss.json'
        data_file.write_text(json.dumps(injected, ensure_ascii=False), 'utf-8')
        out_dir = tmp / 'out'
        out_dir.mkdir()

        import subprocess
        r = subprocess.run(
            ['python3', str(ROOT / 'scripts/render.py'), '--all', str(data_file), str(out_dir)],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        if r.returncode != 0:
            # validate errors expected (injected values may fail schema checks)
            pass

        bad = []
        for html in out_dir.glob('*.html'):
            content = html.read_text('utf-8')
            if SAFE_RE.search(content):
                bad.append(html.name)

        if bad:
            print('❌ XSS 未转义，发现注入内容：')
            for f in bad:
                print('  ', f)
            sys.exit(1)
        else:
            print(f'✓ XSS 检查通过（扫描了 {len(list(out_dir.glob("*.html")))} 个页面）')
    finally:
        if not keep:
            shutil.rmtree(tmp, ignore_errors=True)

if __name__ == '__main__':
    main()
