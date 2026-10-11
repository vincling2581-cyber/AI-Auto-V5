/* Current-episode scenes. Motion follows the reference's object/path grammar;
   the copy, timing, and relations belong only to this Skill episode. */
(()=>{
  const K=window.CardKit;
  const {lerp,phase,m,box,panel,text,group,clip,settle,path,icon,packet,morph,folder}=K;

  window.cardScenes.C07=t=>{
    const labels=['使用条件','执行步骤','注意事项','合格结果'];
    const symbols=['target','grid','sliders','check'];
    const starts=[.05,.83,1.63,2.8],ys=[355,492,629,766];
    let routes='',sources='',rows='';
    // Four independent sources remain parallel; none points to another source.
    labels.forEach((label,i)=>{
      const a=starts[i], y=ys[i], endY=455+i*95;
      const d=`M620 ${y}C792 ${y} 860 ${endY} 1047 ${endY}`;
      routes+=path(d,m(t,a+.10,.60),'line',3);
      routes+=packet(d,phase(t,a+.24,.62),'accent',8);
      const node=panel(150,y-53,470,106,'dark',22)+
        icon(symbols[i],182,y-37,72,'accent',m(t,a,.58))+
        text(label,291,y+17,46,'text');
      sources+=clip(node,m(t,a,.32),142,y-61,487,123);
      rows+=clip(icon(symbols[i],1090,endY-28,54,'accent',m(t,a+.84,.38))+
        text(label,1173,endY+16,46,'text'),m(t,a+.86,.36),1086,endY-42,605,89);
      rows+=path(`M1100 ${endY+38}H1715`,m(t,a+.86,.46),'#335D41',2);
    });
    const sheet=box(1047,291,740,561,'#163420','#60906E',25)+
      icon('clipboard',1092,309,76,'accent',m(t,.02,.65))+
      text('工作手册',1192,366,52,'accent','start',true)+
      path('M1096 394H1735',m(t,.1,.55),'#42674C',2)+rows;
    return routes+sources+settle(sheet,t,0,.5,1417,571,{dy:12,scale:.985,rotate:-.5});
  };

  window.cardScenes.C09=t=>{
    let s='';
    // The two misconceptions are explicitly crossed out, then leave room for
    // the actual four components. They never become inputs to the file.
    const intro=1-m(t,2.72,.36);
    s+=group(text('一句提示词',548,468,48,'muted','middle')+
      text('“认真一点”',1372,468,48,'muted','middle')+
      path('M337 449H759',m(t,.65,.5),'#B99079',4)+
      path('M1158 449H1586',m(t,1.8,.5),'#B99079',4),intro);

    const labels=['流程','判断标准','工具用法','验收要求'];
    const symbols=['grid','check','sliders','target'];
    const starts=[3.35,4.35,5.15,5.95];
    const positions=[[130,370],[1390,370],[130,622],[1390,622]];
    const rowsY=[453,532,611,690],archive=m(t,7.58,.88);
    let routes='',nodes='',rows='';
    labels.forEach((label,i)=>{
      const [x,y]=positions[i],left=i%2===0,a=starts[i];
      const sx=left?510:1390,sy=y+52;
      const ex=lerp(left?745:1175,left?889:1031,archive);
      const ey=lerp(rowsY[i]-11,771+(i>1?17:-17),archive);
      const c1=left?650:1270,c2=left?674:1246;
      const incoming=`M${sx} ${sy}C${c1} ${sy} ${c2} ${ey} ${ex} ${ey}`;
      const outgoing=`M${ex} ${ey}C${c2} ${ey} ${c1} ${sy} ${sx} ${sy}`;
      routes+=path(outgoing,m(t,a,.55),'line',3);
      routes+=packet(incoming,phase(t,a+.34,.69),'accent',8);
      const node=panel(x,y,380,105,'dark',22)+
        icon(symbols[i],x+20,y+19,65,'accent',m(t,a+.12,.5))+
        text(label,x+113,y+68,46,'text');
      nodes+=clip(settle(node,t,a,.62,x+190,y+52,{dx:left?42:-42,dy:0,scale:.96,rotate:0}),m(t,a,.35),x-7,y-6,394,119);
      rows+=clip(icon(symbols[i],786,rowsY[i]-37,48,'ink',m(t,a+1.03,.3))+
        text(label,850,rowsY[i],40,'ink'),m(t,a+1.03,.31),784,rowsY[i]-49,340,65);
      rows+=path(`M788 ${rowsY[i]+19}H1131`,m(t,a+1.03,.34),'paperLine',2);
    });
    s+=routes+nodes;
    const paper=panel(745,333,430,420,'paper',15)+
      text('工作方法',786,397,44,'ink','start',true)+
      path('M785 417H1134',1,'paperLine',2)+rows;
    s+=group(settle(paper,t,3.25,.42,960,543,{dy:10,scale:.985,rotate:-.5}),m(t,3.42,.13)*(1-m(t,7.58,.20)));
    s+=morph('doc','paper',t,2.95,.6,[875,409,170,185],[745,333,430,420],'paper','paper','accent',32,false);
    const open=m(t,7.20,.46)*(1-m(t,8.55,.44));
    const folderIn=m(t,7.15,.4);
    s+=clip(folder(835,664,250,open,'accent','dark'),folderIn,845,695,233,180,'y');
    // One filled work document shrinks into the open folder. The paper's real
    // silhouette, scale and position change; the source fields stay visible.
    s+=morph('paper','doc',t,7.58,.88,[745,333,430,420],[878,719,164,143],'paper','paper','accent',26,true);
    // Front flap is above the receiving paper, so the archive has actual depth.
    if(t>7.15){
      const fy=664+(43-12*open)*2.5;
      s+=clip(`<path d="M865 ${fy}H1055L${1055-15*open} 869H${865+15*open}Z" fill="#14271B" stroke="#78EFA2" stroke-width="7.5" stroke-linejoin="round"/>`,folderIn,845,695,233,180,'y');
      s+=clip(text('Skill',960,839,46,'accent','middle',true),m(t,8.30,.35),880,791,165,59);
    }
    s+=clip(text('文件 / 文件夹 · 可以重复执行',960,903,34,'accent','middle'),m(t,8.33,.45),592,865,738,50);
    return s;
  };

  window.cardScenes.C10=t=>{
    let s=text('结构示意 · 具体内容按任务配置',124,260,34,'muted');
    s+=folder(170,363,330,m(t,.15,.38)*(1-m(t,1.05,.35)),'accent','dark');
    s+=text('Skill',335,686,48,'accent','middle',true);
    const mainRoute='M462 520C570 520 616 462 733 462';
    s+=path(mainRoute,m(t,.28,.73),'line',3);
    s+=packet(mainRoute,phase(t,.42,.77),'accent',8);
    const labels=['名称','适用场景','执行步骤'];
    const descriptions=['这个 Skill 叫什么','什么情况下使用','具体怎么执行'];
    const starts=[2.7,4.0,5.8];
    let rows='';
    labels.forEach((label,i)=>{
      const y=450+i*79,p=m(t,starts[i],.7);
      rows+=clip(text(label,790,y,44,'text')+text(descriptions[i],1100,y,36,'muted'),p,785,y-52,960,68);
      rows+=path(`M1095 ${y+22}H1734`,p,'#3F6349',2);
    });
    const main=box(735,306,1075,367,'#163420','#639D76',25)+
      icon('doc',781,326,69,'accent',m(t,1.04,.52))+
      text('SKILL.md',878,382,52,'accent','start',true)+
      path('M788 409H1741',m(t,1.1,.54),'#42674C',2)+rows;
    s+=group(settle(main,t,1.0,.4,1272,490,{dy:12,scale:.99,rotate:-.4}),m(t,1.05,.15));
    s+=morph('doc','paper',t,.35,.85,[409,419,126,151],[735,306,1075,367],'paper','#163420','accent',36,false);

    const attachments=['案例库','参考资料','脚本','数据库'];
    const icons=['copy','doc','play','grid'],xs=[740,1040,1340,1640];
    s+=clip(text('复杂 Skill',172,790,34,'muted')+text('可按需配套',172,836,34,'muted'),m(t,7.15,.45),165,743,370,111);
    attachments.forEach((label,i)=>{
      const x=xs[i],a=7.66+i*.38;
      const d=`M462 614C547 614 560 710 620 710H${x-28}Q${x} 710 ${x} 738V747`;
      s+=path(d,m(t,7.10+i*.12,.7),'line',3);
      s+=packet(d,phase(t,a,.81),'accent',8);
      const node=panel(x-128,751,256,136,'dark',19)+
        icon(icons[i],x-32,760,64,'accent',m(t,a+.40,.51))+
        text(label,x,865,44,'text','middle');
      // Each node unfolds below its own branch. The shared origin is carried
      // by the connecting geometry; cards do not fly across earlier labels.
      const arriving=settle(node,t,a,.82,x,821,{dx:0,dy:-20,scale:.91,rotate:0});
      s+=clip(arriving,m(t,a,.30),x-135,727,270,167);
    });
    return s;
  };
})();
