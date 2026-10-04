// Inspect the exported model and the self-contained design report.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const out = path.resolve(__dirname, '../../exports/laptop-stand-sculpted');

(async () => {
  const browser = await chromium.launch({channel:'msedge',headless:true,
    args:['--enable-unsafe-swiftshader']});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000}});
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.goto('http://localhost:3000/?model=laptop-stand-sculpted');
    await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('laptop-stand-sculpted.stl'),{timeout:30000});
    const viewer=await page.evaluate(()=>({selected:document.querySelector('#model-select').value,
      status:document.querySelector('#status').textContent,
      canvas:[document.querySelector('canvas').width,document.querySelector('canvas').height]}));
    await page.screenshot({path:path.join(out,'viewer.png')});
    if(viewer.selected!=='laptop-stand-sculpted'||!viewer.canvas.every(v=>v>0)||errors.length)throw Error(JSON.stringify({viewer,errors}));
    const results={viewer,errors,report:[]};
    if(fs.existsSync(path.join(out,'design-report.html'))) {
      for (const [theme,width,height] of [['light',1440,1000],['dark',1440,1000],['light',375,900]]) {
        await page.setViewportSize({width,height});
        await page.emulateMedia({colorScheme:theme});
        await page.goto('http://localhost:3000/exports/laptop-stand-sculpted/design-report.html');
        await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0));
        const layout=await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,
          viewport:innerWidth,images:document.images.length,broken:Array.from(document.images).filter(i=>!i.naturalWidth).length,
          background:getComputedStyle(document.body).backgroundColor,text:document.body.innerText}));
        await page.screenshot({path:path.join(out,`report-${theme}-${width}-top.png`)});
        await page.screenshot({path:path.join(out,`report-${theme}-${width}.png`),fullPage:true});
        if(layout.scrollWidth>width||layout.broken||layout.images<8)throw Error(JSON.stringify(layout));
        results.report.push({theme,width,...layout});
      }
    }
    fs.writeFileSync(path.join(out,'browser-qa.json'),JSON.stringify(results,null,2),'utf8');
    console.log(JSON.stringify({viewer,errors,report:results.report.map(({text,...rest})=>rest)},null,2));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
