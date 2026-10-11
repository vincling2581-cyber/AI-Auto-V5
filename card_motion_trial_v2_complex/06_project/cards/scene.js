/* Isolated complex-card visual trial. All motion is addressed by frame number. */
(()=>{
  let CFG,DATA,K;
  const clamp=x=>Math.max(0,Math.min(1,x));
  const smooth=x=>{const p=clamp(x);return p*p*(3-2*p)};
  const out=x=>1-Math.pow(1-clamp(x),3);
  const mix=(a,b,p)=>a+(b-a)*p;
  const txt=(s,x,y,size=46,ink='text',anchor='start',bold=true)=>K.text(s,x,y,size,ink,anchor,bold);
  const pathCache=new Map();
  function point(d,p){
    if(!pathCache.has(d)){const el=document.createElementNS('http://www.w3.org/2000/svg','path');el.setAttribute('d',d);pathCache.set(d,el)}
    const el=pathCache.get(d);return el.getPointAtLength(el.getTotalLength()*clamp(p));
  }
  function corners(x,y,w,h,ink='accent',width=3){
    const z=17;
    return `<path d="M${x} ${y+z}V${y}H${x+z}M${x+w-z} ${y}H${x+w}V${y+z}M${x+w} ${y+h-z}V${y+h}H${x+w-z}M${x+z} ${y+h}H${x}V${y+h-z}" fill="none" stroke="${K.col(ink)}" stroke-width="${width}"/>`;
  }
  function titleLayer(repaired,split){
    let s=K.group(K.box(15,18,530,105,'paper','paperLine',12),split);
    // A readable SimSun placeholder changes to the chosen font only after arrival.
    const family=repaired>=1?CFG.type.family:'SimSun';
    s+=`<text x="34" y="87" font-family="${family}" font-size="64" font-weight="${repaired>=1?700:400}" fill="${K.col('ink')}">山野计划</text>`;
    s+=`<text x="38" y="118" font-family="${CFG.type.family}" font-size="18" letter-spacing="5" fill="${K.col('ink')}">FIELD NOTES</text>`;
    return s;
  }
  function background(){
    const hills=`<circle cx="397" cy="186" r="63" fill="${K.col('accent')}"/>
      <path d="M28 339L182 169L325 339Z" fill="${K.col('line')}"/>
      <path d="M162 340L357 143L532 340Z" fill="${K.col('edge')}"/>
      <path d="M236 340L421 228L532 310V340Z" fill="${K.col('ink')}"/>
      <path d="M28 319Q185 255 319 304T532 298" fill="none" stroke="${K.col('paper')}" stroke-width="2" opacity=".45"/>`;
    return K.box(0,0,560,396,'paper','paperLine',18)
      +K.box(28,141,504,203,'muted','none',12)
      +`<defs><clipPath id="poster_window"><rect x="28" y="141" width="504" height="203" rx="12"/></clipPath></defs><g clip-path="url(#poster_window)">${hills}</g>`
      +txt('自然 / 观察 / 记录',34,376,24,'ink','start',false);
  }
  function tag(){return K.box(330,279,190,59,'accent','ink',10)+txt('即刻出发',425,319,32,'ink','middle')}
  function scene(c,frame){
    const raw=id=>{const e=c.process_events.find(e=>e.id===id);return clamp((frame-e.start_frame)/(e.end_frame_exclusive-e.start_frame))};
    const imp=raw('import'),separate=smooth(raw('split')),rebuild=smooth(raw('rebuild'));
    const spread=separate*(1-rebuild),inspect=raw('inspect'),focus=out(raw('focus'));
    const repair=raw('repair'),travel=smooth(repair),repaired=repair>=.86?1:0;
    const editing=raw('edit'),drag=smooth((editing-.15)/.65),dragX=-194*drag;
    const card=c.process_events;
    let s=K.box(0,0,1920,1080,'background','none',0);
    let grid='';for(let x=96;x<1920;x+=96)grid+=`<path d="M${x} 205V908"/>`;
    s+=`<g stroke="${K.col('accent')}" stroke-width="1" opacity=".022">${grid}</g>`;
    s+=K.clip(txt(c.title,100,156,72),out(frame/12),94,70,1650,115);
    s+=txt('结构恢复 / 流程示意',1810,153,30,'muted','end',false);
    s+=K.panel(100,257,1000,641,'dark')+K.panel(1140,257,680,641,'paper');
    s+=txt('编辑画布',158,336,46)+txt('结构检查',1196,336,46,'ink');
    s+=K.group(txt('3 个独立对象',1040,334,30,'muted','end',false),out(raw('split')/.5));

    // The source file survives the import and all later operations.
    s+=K.box(1190,790,580,78,'paper','paperLine',14)
      +K.icon('doc',1202,800,62,'ink',1)+txt('示例海报工程',1292,842,34,'ink');

    const px=248,py=410;
    const bgX=px-62*spread,bgY=py+17*spread;
    const titleX=px+116*spread,titleY=py-43*spread;
    const tagX=px+148*spread,tagY=py+56*spread;
    const assembled=background()+titleLayer(0,0)+tag();
    if(imp<=0)s+=txt('等待导入',600,604,42,'muted','middle',false);
    if(imp>0&&imp<1){
      const route='M1240 822C1050 835 700 550 528 608',q=smooth(imp),xy=point(route,q);
      const scale=mix(.12,1,q);
      s+=K.group(K.path(route,q,'line',3),Math.sin(Math.PI*imp)*.65);
      s+=`<g transform="translate(${xy.x},${xy.y}) rotate(${7*(1-q)}) scale(${scale}) translate(-280,-198)">${assembled}</g>`;
    }
    if(imp>=1){
      // Background, title and tag are retained as three separately addressable objects.
      s+=K.group(background(),1,bgX,bgY,1,-3.2*spread,280,198);
      const titleBody=titleLayer(repaired,spread);
      s+=K.group(titleBody,1,titleX,titleY,1,1.2*spread,280,70);
      s+=K.group(tag(),1,tagX+dragX,tagY,1,-2.2*spread,425,309);
      if(spread>0){
        s+=K.group(corners(titleX+10,titleY+12,540,116,'accent'),spread);
        s+=K.group(K.path(`M${titleX+26} ${titleY+134}H${titleX+532}`,1,'muted',2),spread*.7);
      }
    }

    // Inspection rows carry graphic thumbnails that match the actual layer contents.
    const rowSpecs=[['背景','图形保留'],['标题',repaired?'字体已替换':'检查字体'],['标签',editing>=.8?'位置已更新':'位置保留']];
    const rowYs=[384,486,588];
    for(let i=0;i<3;i++){
      const appear=out((raw('split')-i*.18)/.64),y=rowYs[i];
      let body=K.box(1190,y,580,88,'paper',i===1&&focus>0&&!repaired?'ink':'paperLine',14);
      body+=K.box(1208,y+17,70,54,i===1?'accent':'dark','none',8);
      if(i===0)body+=`<path d="M1216 ${y+62}L1236 ${y+32}L1250 ${y+51}L1268 ${y+28}V${y+63}Z" fill="${K.col('accent')}"/>`;
      if(i===1)body+=txt('Aa',1243,y+56,31,'ink','middle');
      if(i===2)body+=K.box(1217,y+32,52,23,'accent','none',5);
      body+=txt(rowSpecs[i][0],1304,y+55,38,'ink');
      const confirm=out((inspect-i*.13)/.6);
      const label=i===1&&focus>0&&!repaired?'字体缺失':rowSpecs[i][1];
      body+=K.group(txt(label,1738,y+54,30,'ink','end',false),confirm);
      s+=K.group(body,appear);
    }

    // Brief tracing relates the visible layers to their records; no unrelated objects move.
    const trace=Math.sin(Math.PI*inspect)*spread;
    if(inspect>0&&inspect<1){
      const targets=[[bgX+554,bgY+280,428],[titleX+544,titleY+73,530],[tagX+520,tagY+309,632]];
      for(let i=0;i<3;i++){
        const [x,y,ey]=targets[i],p=out((inspect-i*.1)/.7),route=`M${x} ${y}C1080 ${y} 1080 ${ey} 1190 ${ey}`;
        s+=K.group(K.path(route,p,'line',2),trace*.65);
        const xy=point(route,p);if(p>0&&p<1)s+=`<circle cx="${xy.x}" cy="${xy.y}" r="5" fill="${K.col('accent')}"/>`;
      }
    }

    // Local repair drawer stays associated with the title row.
    const drawer=focus*(1-out(raw('rebuild')/.6));
    if(drawer>0){
      const content=K.box(1190,694,580,75,'dark','edge',12)
        +txt(repaired?'替换完成，关系保留':'替换字体',1214,742,repaired?32:34,'text')
        +(repaired?K.icon('check',1702,710,42,'accent'):txt('微软雅黑',1735,742,34,'accent','end'));
      s+=K.clip(content,drawer,1188,692,584,79);
      if(!repaired){
        const route=`M1478 730C1300 735 1180 365 ${titleX+270} ${titleY+73}`;
        const q=smooth(repair/.86),xy=point(route,q);
        if(repair>0&&repair<.86){
          const scale=(.7+.3*Math.sin(Math.PI*q))*(1-smooth((repair-.78)/.08));
          s+=K.group(K.path(route,q,'line',3),Math.sin(Math.PI*q)*.65);
          const token=K.box(-49,-31,98,62,'accent','ink',10)+txt('Aa',0,14,38,'ink','middle');
          s+=K.group(token,out(repair/.06),xy.x,xy.y,scale);
        }
      }
    }

    // Arrival triggers the same title's weight change with a local horizontal reveal.
    if(repair>=.86&&repair<1&&imp>=1){
      const p=out((repair-.86)/.14);
      const fixed=titleLayer(1,spread);
      const old=titleLayer(0,spread);
      const reveal=K.clip(fixed,p,10,10,540,126);
      s+=K.group(old+reveal,1,titleX,titleY,1,1.2*spread,280,70);
    }

    const isReady=raw('rebuild')>=1;
    if(isReady){
      const enter=out((frame-402)/12);
      s+=K.group(K.icon('check',1201,704,47,'ink')+txt('结构完整，可继续编辑',1271,743,36,'ink'),enter);
    }
    // Final editing changes only the tag, leaving a deliberate new settled composition.
    if(editing>0&&imp>=1){
      const select=out(editing/.1),x=px+330+dragX,y=py+279;
      s+=K.group(corners(x-8,y-8,206,75,'ink',3),select);
      const guides=out((editing-.45)/.15)*(1-out((editing-.86)/.14));
      s+=K.group(K.path(`M${px+136} ${py+139}V${py+351}`,1,'accent',2)+K.path(`M${px+28} ${py+338}H${px+532}`,1,'accent',2),guides);
      const cursor=`<path d="M0 0V34L9 25L17 42L25 38L18 23L34 22Z" fill="${K.col('paper')}" stroke="${K.col('ink')}" stroke-width="2.5" stroke-linejoin="round"/>`;
      s+=K.group(cursor,select*(1-out((editing-.86)/.14)),x+149,y+37);
    }

    // Four stable stage anchors guide reading without repeating the narration.
    const stages=[['导入',raw('import')],['识别',raw('inspect')],['修复',repair],['继续编辑',editing]];
    for(let i=0;i<4;i++){
      const x=128+i*438,done=stages[i][1]>=1,active=stages[i][1]>0;
      if(i<3)s+=K.path(`M${x+236} 951H${x+389}`,1,'edge',2);
      s+=`<circle cx="${x}" cy="951" r="20" fill="${K.col(done?'accent':'soft')}" stroke="${K.col(active?'accent':'edge')}" stroke-width="2"/>`;
      s+=done?K.icon('check',x-16,935,32,'ink'):txt(String(i+1),x,960,24,active?'accent':'muted','middle');
      s+=txt(stages[i][0],x+38,963,34,active?'text':'muted');
    }
    s+=txt('对象关系始终保留，只处理出现问题的部分',100,1016,34,'muted','start',false);
    s+=txt('示例流程',1818,1016,30,'muted','end',false);
    window.motionState={frame,imported:imp>=1,spread,titleAnchor:[titleX,titleY],backgroundAnchor:[bgX,bgY],
      tagAnchor:[tagX+dragX,tagY],repaired:!!repaired,sourceFileRetained:true,layerCount:3,editable:isReady};
    return s;
  }
  window.renderFrame=async(frame,cardId='C01')=>{
    const c=DATA.cards.find(c=>c.id===cardId)||DATA.cards[0];
    const f=Math.max(0,Math.min(c.frame_count-1,Math.round(frame)));
    K.beginFrame();document.getElementById('scene').innerHTML=scene(c,f);
    window.lastRendered={id:c.id,frame:f};return window.lastRendered;
  };
  window.readyPromise=(async()=>{
    [CFG,DATA]=await Promise.all([fetch('../../00_brief/effective_defaults.json').then(r=>r.json()),fetch('../../03_storyboard/cards.json').then(r=>r.json())]);
    K=createReferenceCardKit(CFG);await document.fonts.ready;window.effectiveCardProfile=K.profile();
    await window.renderFrame(0);window.cardMotionReady=true;
  })();
})();
