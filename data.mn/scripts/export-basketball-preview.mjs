import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// A portable, offline review artifact built from the same source as the Astro page.
const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.resolve(site, '../outputs/basketball-site-preview');
const translations = fs.readFileSync(path.join(site, 'src/i18n/sports.ts'), 'utf8');
const { sports } = await import(`data:text/javascript;base64,${Buffer.from(translations).toString('base64')}`);
const data = fs.readFileSync(path.join(site, 'public/sports/basketball.json'), 'utf8');
const css = fs.readFileSync(path.join(site, 'src/assets/styles/sports.css'), 'utf8');
const js = fs
  .readFileSync(path.join(site, 'src/scripts/sports-browser.js'), 'utf8')
  .replace(/^export /gm, '')
  .replace(
    "fetch('/sports/basketball.json')",
    "Promise.resolve({ok:true,json:async()=>JSON.parse(document.getElementById('sp-embedded-data').textContent)})"
  )
  .replace('href="/${lang}/sports/basketball"', 'href="?lang=${lang}"');
const safe = (value) => JSON.stringify(value).replace(/</g, '\\u003c');
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Basketball | data.mn — Preview</title><style>
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,sans-serif;background:#fff;color:#172841}button,a{color:inherit}a{text-decoration:none}button{cursor:pointer}.preview-header{height:72px;display:flex;align-items:center;justify-content:space-between;padding:0 35px;border-bottom:1px solid #e4e9f0;position:sticky;top:0;z-index:5;background:#fff}.preview-logo{font-size:24px;font-weight:750;letter-spacing:-1px}.preview-logo span{color:#2563eb;margin-right:8px}.preview-header nav{display:flex;gap:30px;font-size:13px}.preview-header nav a.active{color:#2563eb;border-bottom:2px solid #2563eb;padding-bottom:10px}.preview-header aside{display:flex;gap:15px;align-items:center;font-size:11px}.preview-header button{background:none;border:1px solid #dce3ee;padding:5px 10px;border-radius:4px;font-size:12px}.dark body,.dark .preview-header{background:#090f24;color:#e6ecf6}.dark .preview-header{border-color:#29374e}.dark .preview-header button{border-color:#344763}.preview-header .active-lang{font-weight:700;color:#2563eb}@media(max-width:650px){.preview-header{padding:0 17px;height:62px}.preview-header nav{display:none}.preview-logo{font-size:21px}}
${css}
</style></head><body><header class="preview-header"><a class="preview-logo" href="https://data.mn"><span>⌁</span>Data.mn</a><nav id="preview-nav"></nav><aside><a href="?lang=mn" id="mn-link">MN</a><a href="?lang=en" id="en-link">EN</a><button id="preview-theme" aria-label="Change color theme">◐</button></aside></header><div id="sports-app"></div><script id="sp-embedded-data" type="application/json">${data.replace(/</g, '\\u003c')}</script><script>
const language=new URLSearchParams(location.search).get('lang')==='mn'?'mn':'en';
document.documentElement.lang=language;
const ui=${safe(sports)};
const root=document.getElementById('sports-app');root.dataset.language=language;root.dataset.copy=JSON.stringify(ui[language]);
document.getElementById(language+'-link').className='active-lang';
document.getElementById('preview-nav').innerHTML=[['data',language==='mn'?'Өгөгдөл':'Data'],['sports',ui[language].sport],['insights',language==='mn'?'Нийтлэл':'Insights'],['about',language==='mn'?'Бидний тухай':'About']].map(([p,l])=>'<a class="'+(p==='sports'?'active':'')+'" href="'+(p==='sports'?'?lang='+language:'https://data.mn/'+language+'/'+p)+'">'+l+'</a>').join('');
document.getElementById('preview-theme').onclick=()=>document.documentElement.classList.toggle('dark');
${js.replace(/<\/script/gi, '<\\/script')}
</script></body></html>`;
fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, 'basketball-preview.html'), html);
console.log(path.join(out, 'basketball-preview.html'));
