scenes.C04=(c,t)=>{
  // Trial-local choreography. Event windows and settled artwork are unchanged.
  const frame=Math.round(t*DATA.fps);
  const raw=id=>{const e=E(c,id);return clamp((frame-e.start_frame)/(e.end_frame_exclusive-e.start_frame));};
  const smooth=p=>p*p*(3-2*p);
  const out=p=>1-Math.pow(1-clamp(p),3);
  const pulse=p=>p>0&&p<1?Math.pow(Math.sin(Math.PI*p),2):0;
  const sv=raw('save'),cl=raw('close'),op=raw('open'),rs=raw('restore');
  const lp=raw('layers'),pp=raw('position'),wp=raw('workflow');
  const route='M822 500C1020 375 1300 365 1415 470';
  // SVG arc length keeps both trips on the exact same curved route.
  const path=document.createElementNS('http://www.w3.org/2000/svg','path');
  path.setAttribute('d',route);
  const length=path.getTotalLength();
  const point=p=>path.getPointAtLength(length*clamp(p));
  const mask=(content,id,x,y,w,h)=>`<defs><clipPath id="c04_${id}"><rect x="${x}" y="${y}" width="${Math.max(0,w)}" height="${Math.max(0,h)}"/></clipPath></defs><g clip-path="url(#c04_${id})">${content}</g>`;
  // A three-layer copy preserves the middle green layer's identity in both directions.
  const packet=(p,reverse=false)=>{
    if(p<=0||p>=1)return '';
    const travel=smooth(p),pos=point(reverse?1-travel:travel);
    const a=point((reverse?1-travel:travel)-.005),b=point((reverse?1-travel:travel)+.005);
    const angle=Math.atan2(b.y-a.y,b.x-a.x)*180/Math.PI*.22;
    const scale=out(p/.16)*(1-smooth(clamp((p-.78)/.22)));
    let body='';
    for(let i=0;i<3;i++)body+=K.box(-44,-29+i*21,88,16,i===1?'accent':'paper','edge',5);
    return K.group(body,1,pos.x,pos.y,scale,angle);
  };
  let s=K.panel(100,265,780,630,'dark')+K.panel(1040,265,780,630,'paper');
  s+=T('编辑结构',160,345,50)+T('工程文件',1100,345,50,'ink');

  const editing=32*pulse(wp);
  let content=art(155,395,422,338,0,editing);
  if(rs>0&&rs<1){
    const reveal=out((rs-.10)/.90);
    content=mask(content,'art_restore',153+426*(1-reveal),393,426*reveal,342);
  }
  const labels=['背景','主体','文字'];
  for(let i=0;i<3;i++){
    const spread=pulse(lp),dx=[-12,22,-12][i]*spread,dy=(i-1)*18*spread;
    let layer=K.box(602+dx,424+i*76+dy,220,58,i===1?'accent':'paper','paperLine',12)
      +T(labels[i],626+dx,465+i*76+dy,34,'ink');
    if(rs>0&&rs<1){
      const delay=[.10,0,.20][i],reveal=out((rs-delay)/(1-delay));
      layer=mask(layer,'layer_'+i,600+224*(1-reveal),422+i*76,224*reveal,62);
    }
    content+=layer;
  }
  // Closing crops the content into a horizontal seam; its opacity stays solid.
  if(cl>0&&rs<=0){
    const remaining=1-smooth(cl);
    content=mask(content,'close',153,564-172*remaining,674,344*remaining);
  }
  // Clear the closed-state label before restoration, avoiding partially covered text.
  const closed=smooth(cl)*(1-smooth(clamp((op-.68)/.32)));
  s+=hide(K.icon('folder',408,505,126,'muted',1)+T('已关闭',475,733,40,'muted','middle'),closed);
  s+=hide(content,1);

  // The archive remains present throughout close, reopen and restored editing.
  s+=K.icon('doc',1335,393,160,'ink',out(sv/.88))+T('.comp',1415,582,44,'ink','middle');
  s+=line(route,clamp(smooth(sv)*1.6),'line',4);
  s+=packet(sv)+packet(op,true);
  const receipt=pulse(clamp((sv-.65)/.35));
  if(receipt>0)s+=hide(K.box(1366,406,98,135,'none','ink',8),receipt*.65);

  const vals=[['图层结构','layers'],['对象位置','position'],['继续编辑','workflow']];
  for(let i=0;i<vals.length;i++){
    const p=raw(vals[i][1]),check=out(p/.55),label=out((p-.16)/.84);
    s+=hide(K.icon('check',1120,653+i*64,40,'ink',check),check);
    s+=hide(row(vals[i][0],1190,688+i*64,520,'ink',label),label);
  }
  // Selected layer follows the short layer inspection, then settles at the old anchor.
  s+=hide(K.box(593+22*pulse(lp),490,233,78,'none','accent',12),out(rs));

  // Coordinate guides reference the original position without moving the object.
  const guide=pulse(pp);
  if(guide>0){
    const corners='M285 489H263V511M418 511V489H396M263 663V685H285M396 685H418V663';
    s+=hide(line(corners,out(pp/.6),'ink',3)
      +line('M361.78 395V733M155 557.24H577',1,'ink',1.5),guide*.7);
    s+=hide(line('M418 529H602',out(pp/.65),'accent',3),guide);
  }
  // The final event demonstrates a reversible edit; restoration itself never drifts.
  const editVisible=pulse(wp);
  if(editVisible>0){
    s+=hide(K.box(263+editing,489,155,196,'none','ink',5),editVisible*.8);
    const cursor=`<path d="M0 0L0 31L8 23L15 37L23 33L16 20L29 19Z" fill="${K.col('paper')}" stroke="${K.col('ink')}" stroke-width="2.5" stroke-linejoin="round"/>`;
    s+=K.group(cursor,out(wp/.12)*(1-out((wp-.83)/.17)),405+editing,594);
  }
  s+=F('保存 → 关闭 → 重开：恢复相同对象与位置　·　流程示意');
  return s;
};
