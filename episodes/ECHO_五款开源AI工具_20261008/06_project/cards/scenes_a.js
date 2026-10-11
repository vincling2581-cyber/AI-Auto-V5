(()=>{
const names=['VoiceStudio','Paperclip','MemOS','Ollama + WebUI','Impeccable'],jobs=['声音制作','任务协作','长期记忆','本地模型','界面设计'];
SCENES.C00=t=>{let s='';const{box,text,ease,group}=H;let p=ease(t,2.15,.95);
for(let i=0;i<5;i++){const q=ease(t,.10+i*.12,.65),x=110+i*348,y=360+(1-p)*(i%2?60:0);s+=group(box(x,y,320,350,i%2?'#F0F3EC':'#14271B',i%2?'none':'#34533C')+text('0'+(i+1),x+28,y+65,38,i%2?'#537D5E':'#78EFA2')+H.k.icon(['play','clipboard','folder','chat','grid'][i],x+110,y+97,100,i%2?'#285239':'#78EFA2')+text(names[i],x+160,y+250,i===3?34:40,i%2?'#24362B':'#F0F3EC',true,'middle')+text(jobs[i],x+160,y+310,34,i%2?'#52705A':'#A1C4AB',false,'middle'),0,(1-q)*90,q);}
s+=group(text('先找到用途，再核对授权',960,854,54,'#78EFA2',true,'middle'),0,35*(1-ease(t,3.55,.65)),ease(t,3.55,.65));return s;};
const waveform=(x,y,w,h,progress,color='#78EFA2')=>Array.from({length:31},(_,i)=>{const a=(.2+.8*Math.abs(Math.sin(i*1.31)))*h;return `<rect x="${x+i*w/31}" y="${y-a/2}" width="${w/50}" height="${a}" rx="4" fill="${color}" opacity="${i/31<progress?1:.15}"/>`}).join('');
SCENES.C01=t=>{const{box,text,ease,phase,line,dot,group}=H;let s=box(90,282,740,640)+box(870,282,960,640,'#F0F3EC','none');
if(t<4.8){s+=H.tag('参考录音',128,320,194)+text('3 秒',160,475,100,'#78EFA2',true)+text('输入音频长度',164,532,34,'#A1C4AB')+waveform(155,630,540,116,ease(t,.3,1.6));
 const d='M738 602 C830 602 918 526 1050 526';s+=line(d,'#78EFA2',6,phase(t,1.3,1.0))+dot(d,phase(t,1.3,1.0),15);
 s+=text('同款音色档案',1095,378,46,'#24362B',true)+box(1025,430,640,308,'#DBEBDD','none')+H.k.icon('person',1060,466,138,'#315C3D');
 s+=group(waveform(1250,552,340,100,1,'#315C3D')+text('音色特征已提取',1340,694,38,'#315C3D',false,'middle'),0,24*(1-ease(t,2.3,.7)),ease(t,2.3,.7));
 s+=text('仅指参考时长，不是生成耗时',1008,826,34,'#52705A');
 if(t>3.0){const labels=['口播','播客','有声书'];for(let i=0;i<3;i++)s+=group(H.tag(labels[i],133+i*218,770,196),0,20*(1-ease(t,3.1+i*.15,.5)),ease(t,3.1+i*.15,.5));}
}else if(t<8.05){s+=text('多语言 × 多音色',133,364,48,'#F0F3EC',true);
const langs=['中文','English','日本語'];for(let i=0;i<3;i++){let q=ease(t,4.9+i*.65,.5);s+=group(box(135,409+i*144,650,108,'#203D2B','none',20)+text(langs[i],171,475+i*144,40,'#F0F3EC',true)+waveform(411,463+i*144,324,53,1),-(1-q)*32,0,q);}
s+=text('VoiceStudio · 官方界面',919,357,36,'#315C3D',true)+H.img('official/voice_clone.webp',911,393,878,457)+text('声音克隆界面示例',1310,892,30,'#52705A',false,'middle');
}else{const q=ease(t,8.15,.6);s+=text('从声音到成品',132,367,52,'#F0F3EC',true)+H.img('official/voice_dub.webp',125,419,670,370)+text('官方配音界面示例',145,864,32,'#A1C4AB');
s+=group(text('使用前核对',934,370,50,'#24362B',true)+text('软件授权',949,472,36,'#52705A')+text('AGPL-3.0',949,535,50,'#24362B',true)+line('M940 572H1730','#B3C8B8',2)+text('模型权重许可另算',949,646,46,'#24362B',true)+text('默认 OmniVoice：CC-BY-NC',949,714,34,'#915B34')+text('含非商用限制',949,760,30,'#915B34')+group(box(927,782,802,96,'#CFE1D4','none',18)+text('商业使用需另查授权',949,846,38,'#315C3D',true),0,0,ease(t,10,.6)),0,(1-q)*30,q);
}return s;};
SCENES.C06=t=>{const{box,text,ease,group}=H;const p=ease(t,0,.65);let s=box(90,290,1740,628,'#F0F3EC','none');s+=group(text('每天了解一个 AI 新玩法',960,535,82,'#24362B',true,'middle')+text('声音  /  协作  /  记忆  /  本地  /  设计',960,659,40,'#52705A',false,'middle')+box(690,744,540,94,'#24452F','none',24)+text('让工具，进入你的工作流',960,803,38,'#F0F3EC',true,'middle'),0,(1-p)*36,p);return s;};
})();
