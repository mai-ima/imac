// handoff/02_PDF/_sources.json の SVG を A3横PDFへ変換する。実行: cd /home/user/imac && node tools/svg2pdf.js (playwright 必須)
const {chromium}=require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{const R=path.resolve(__dirname,'..'); const src=JSON.parse(fs.readFileSync(`${R}/handoff/02_PDF/_sources.json`)).sheets;
 const b=await chromium.launch(); const p=await b.newPage();
 for(const s of src){ const base=path.basename(s,'.svg'); const out= s.startsWith('drawings/parts/')?`parts_${base}.pdf`: s.startsWith('drawings/v10/')?`v10_${base}.pdf`:`${base}.pdf`;
  const svg=fs.readFileSync(`${R}/${s}`,'utf8'); await p.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  await p.pdf({path:`${R}/handoff/02_PDF/${out}`,width:'420mm',height:'297mm',printBackground:true,pageRanges:'1'}); }
 await b.close(); console.log('pdf',src.length);})();
