#!/usr/bin/env python3
"""Machine checks for this episode's full MP4; launch through locked run_stage.py."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import io
import json
import logging
import math
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
QC = ROOT / "08_qc"
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
MASK_PADDING_PX = 2


def digest(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(command, *, binary=False, timeout=240):
    result = subprocess.run(command, capture_output=True, creationflags=NO_WINDOW, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"命令失败({result.returncode})：{command}\n" + result.stderr.decode("utf-8", "replace"))
    return result.stdout if binary else result.stdout.decode("utf-8", "replace")


def chrome_executable():
    candidates = []
    if os.name == "nt":
        import winreg
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as key:
                    candidates.append(Path(winreg.QueryValue(key, None)))
            except OSError:
                pass
        for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            if os.environ.get(env):
                candidates.append(Path(os.environ[env]) / "Google/Chrome/Application/chrome.exe")
    found = shutil.which("chrome") or shutil.which("google-chrome")
    if found:
        candidates.append(Path(found))
    return next((p.resolve() for p in candidates if p.is_file()), None)


def binding_files(config, video, scenes):
    chrome = chrome_executable()
    require(chrome is not None, "无法定位实际 Chrome 可执行文件以绑定工具哈希")
    paths = {
        "video": video,
        "episode": ROOT / "00_brief/episode.json",
        "effective_defaults": config.defaults_path,
        "production_contract": config.contract_path,
        "scenes": ROOT / "03_storyboard/scenes.json",
        "semantic_design": ROOT / "03_storyboard/semantic_design.json",
        "subtitles": ROOT / "02_timing/subtitles.json",
        "index": ROOT / "06_project/index.html",
        "app": ROOT / "06_project/app.js",
        "cards": ROOT / "06_project/cards.js",
        "render_adapter": ROOT / "06_project/render.py",
        "verification_script": Path(__file__),
        "original_voice": config.audio,
        "ffmpeg": config.ffmpeg,
        "ffprobe": config.ffmpeg.with_name("ffprobe.exe" if os.name == "nt" else "ffprobe"),
        "python": Path(sys.executable),
        "chrome": chrome,
    }
    defaults = read_json(config.defaults_path)
    for name in ("regular_font", "bold_font"):
        paths[name] = Path(defaults["type"][name])
    for clip in scenes:
        if clip["layer"] == "illustration":
            paths[clip["id"]] = ROOT / clip["asset_path"]
    return {key: {"path": str(path.resolve()), "sha256": digest(path)} for key, path in paths.items()}


def probe_video(config, video):
    probe = config.ffmpeg.with_name("ffprobe.exe" if os.name == "nt" else "ffprobe")
    command = [str(probe), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)]
    data = json.loads(run(command))
    streams = data["streams"]
    v = next(s for s in streams if s["codec_type"] == "video")
    a = next((s for s in streams if s["codec_type"] == "audio"), None)
    require(v["width"] == config.width and v["height"] == config.height, "成片尺寸与配置不一致")
    require(Fraction(v["r_frame_rate"]) == config.fps, "成片帧率与配置不一致")
    require(int(v["nb_frames"]) == config.total_frames, "此脚本只验本集完整1678帧成片")
    require(abs(float(v["duration"]) - config.total_frames/config.fps) < .5/config.fps, "视频流时长不一致")
    require(v["pix_fmt"] == config.video["pixel_format"], "视频像素格式不一致")
    require(a is not None, "缺少原配音音轨")
    require(abs(float(a.get("start_time", 0))) < 1/config.fps, "配音未从0点起始")
    require(abs(float(v.get("start_time", 0))) < 1/config.fps, "视频未从0点起始")
    return {"passed": True, "command": command, "data": data}


def full_decode(config, video):
    command = [str(config.ffmpeg), "-nostdin", "-hide_banner", "-v", "error", "-xerror", "-i", str(video),
               "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"]
    result = subprocess.run(command, capture_output=True, creationflags=NO_WINDOW, timeout=300)
    log = QC / "output_full_decode.log"
    log.write_bytes(result.stderr)
    require(result.returncode == 0, "全片视频/音频解码失败，见 " + str(log))
    return {"passed": True, "scope": "all_encoded_video_frames_and_audio_packets_decoded",
            "command": command, "returncode": result.returncode,
            "stderr_bytes": len(result.stderr), "log": str(log), "log_sha256": digest(log)}


def audio_check(config, video):
    import numpy as np
    rate = 16000
    def decode(path):
        command = [str(config.ffmpeg), "-nostdin", "-v", "error", "-i", str(path), "-map", "0:a:0",
                   "-ac", "1", "-ar", str(rate), "-c:a", "pcm_f32le", "-f", "f32le", "pipe:1"]
        return np.frombuffer(run(command, binary=True), dtype="<f4").astype(np.float64), command
    original, original_command = decode(config.audio)
    encoded, encoded_command = decode(video)
    require(len(encoded) >= len(original)-rate/config.fps, "成片音频丢失超过一帧的原音尾部")
    n = min(len(original), len(encoded))
    require(n > rate, "有效音频不足1秒")
    a, b = original[:n], encoded[:n]
    a, b = a-a.mean(), b-b.mean()
    require(float(np.dot(a,a)) > 1e-5 and float(np.dot(b,b)) > 1e-5, "原音或成片音轨静音")
    nfft = 1 << (2*n-1).bit_length()
    cross = np.fft.irfft(np.fft.rfft(b,nfft)*np.conj(np.fft.rfft(a,nfft)),nfft)
    lags = np.arange(-rate//2, rate//2+1)
    numerators = cross[np.where(lags>=0,lags,nfft+lags)]
    prefix_a = np.r_[0.,np.cumsum(a*a)]
    prefix_b = np.r_[0.,np.cumsum(b*b)]
    lo_a,hi_a = np.maximum(0,-lags),np.minimum(n,n-lags)
    lo_b,hi_b = np.maximum(0,lags),np.minimum(n,n+lags)
    energy_a = prefix_a[hi_a]-prefix_a[lo_a]
    energy_b = prefix_b[hi_b]-prefix_b[lo_b]
    correlations = numerators/np.sqrt(energy_a*energy_b)
    best = int(np.argmax(correlations))
    zero_corr = float(np.dot(a,b)/math.sqrt(float(np.dot(a,a)*np.dot(b,b))))
    gain = float(np.dot(a,b)/np.dot(a,a))
    rms_ratio = float(math.sqrt(float(np.dot(b,b)/np.dot(a,a))))
    nrmse = float(math.sqrt(float(np.dot(a-b,a-b)/np.dot(a,a))))
    best_lag = int(lags[best])
    checks = {"zero_lag_correlation_at_least_0_99": zero_corr >= .99,
              "peak_within_1ms_of_zero": abs(best_lag) <= rate*.001,
              "estimated_gain_within_2_percent": .98 <= gain <= 1.02,
              "rms_ratio_within_2_percent": .98 <= rms_ratio <= 1.02,
              "normalized_rmse_at_most_0_15": nrmse <= .15}
    return {"passed": all(checks.values()), "checks": checks, "analysis_sample_rate": rate,
            "analysis_channels": "mono", "original_decoded_samples": len(original),
            "output_decoded_samples": len(encoded), "compared_samples": n,
            "zero_lag_correlation": zero_corr, "peak_correlation": float(correlations[best]),
            "best_output_delay_samples": best_lag, "best_output_delay_seconds": best_lag/rate,
            "lag_search_seconds": [-.5,.5], "estimated_linear_gain": gain,
            "rms_ratio": rms_ratio, "normalized_rmse": nrmse,
            "original_decode_command": original_command, "output_decode_command": encoded_command,
            "limit": "有损编码容差下的波形一致性与零点对齐检查；16kHz单声道重采样仅用于分析，不写回音视频，也不是主观试听。"}


def sampling_plan(config, scenes, design):
    frames, illustrations, boundaries, observations = set(), [], set(), []
    for clip in scenes:
        if clip["layer"] != "illustration":
            continue
        first,last = clip["start_frame"],clip["end_frame_exclusive"]-1
        sample = sorted(set((first,(first+last)//2,last)))
        frames.update(sample)
        illustrations.append({"clip": clip, "frames": sample})
        for edge in (clip["start_frame"],clip["end_frame_exclusive"]):
            if 0 < edge < config.total_frames:
                boundaries.add((edge-1,edge))
                frames.update((edge-1,edge))
    card_clips = {c["id"]:c for c in scenes if c["layer"] == "information_card"}
    for card in design["cards"]:
        clip = card_clips[card["cardId"]]
        for second in card["observeAtLocalSeconds"]:
            frame = min(clip["end_frame_exclusive"]-1,clip["start_frame"]+round(second*config.fps))
            frames.add(frame)
            observations.append({"card_id":clip["id"],"requested_local_seconds":second,"frame":frame,
                                 "actual_local_seconds":(frame-clip["start_frame"])/config.fps})
    return sorted(frames),illustrations,sorted(boundaries),observations


FRAME_STATE_JS = """() => {
  const node=document.getElementById('caption'),stage=document.getElementById('stage');
  const c=getComputedStyle(node),r=node.getBoundingClientRect(),s=stage.getBoundingClientRect();
  const scale=s.width/1920;
  const shown=c.display!=='none'&&c.visibility!=='hidden'&&Number(c.opacity)!==0&&node.textContent.length>0;
  return {state:window.getFrameState(),text_bounds:window.inspectTextBounds(),
    caption_rect:shown?{x:(r.x-s.x)/scale,y:(r.y-s.y)/scale,width:r.width/scale,height:r.height/scale}:null,
    caption_css:{display:c.display,padding:c.padding,borderRadius:c.borderRadius,fontSize:c.fontSize,
      lineHeight:c.lineHeight,backgroundColor:c.backgroundColor},
    illustration:Array.from(document.querySelectorAll('#visual img')).map(i=>({src:i.currentSrc,
      complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}))};
}"""


def collect_browser(config, adapter, frames, illustrations, observations):
    from playwright.sync_api import sync_playwright
    import numpy as np
    from PIL import Image
    states,references,errors = {},{},[]
    first_frames = {item["frames"][0]:item["clip"]["id"] for item in illustrations}
    logger = logging.getLogger("verify.http")
    with adapter["local_server"](logger) as url,sync_playwright() as playwright:
        browser=playwright.chromium.launch(channel=config.browser_channel,headless=True,
                                            args=["--force-color-profile=srgb","--hide-scrollbars"])
        try:
            page=browser.new_page(viewport={"width":config.width,"height":config.height},device_scale_factor=1)
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.on("console",lambda m:errors.append(m.text) if m.type=="error" else None)
            page.on("requestfailed",lambda r:errors.append(f"{r.url}: {r.failure}"))
            page.on("response",lambda r:errors.append(f"HTTP {r.status}: {r.url}") if r.status>=400 else None)
            page.goto(url,wait_until="networkidle")
            page.evaluate(adapter["WAIT_READY_JS"])
            for frame in frames:
                page.evaluate(adapter["RENDER_FRAME_JS"],frame)
                data=page.evaluate(FRAME_STATE_JS)
                require(data["state"]["frame"]==frame,"浏览器frameState与指定帧不一致")
                states[frame]=data
                if frame in first_frames:
                    require(data["illustration"] and all(i["complete"] and i["naturalWidth"] for i in data["illustration"]),
                            "插画节点未完成加载："+first_frames[frame])
                    references[first_frames[frame]]=np.array(Image.open(io.BytesIO(page.screenshot(type="png"))).convert("RGB"))
            parameter_probe=check_parameter_consumption(page,config)
            require(not errors,"浏览器资源/脚本异常："+" | ".join(errors))
            for item in observations:
                item["frame_state"]=states[item["frame"]]["state"]
                item["text_bounds_violations"]=states[item["frame"]]["text_bounds"]
            return states,references,{"browser_version":browser.version,"errors":errors},parameter_probe
        finally:
            browser.close()


def check_parameter_consumption(page,config):
    # In-memory probe only. The effective-default file and page app stay unchanged.
    from PIL import Image
    pngs=[]
    values=[]
    for size in (72,64):
        value=page.evaluate("""async size=>{
          const {renderCard}=await import('./cards.js');
          const defaults=await(await fetch('../00_brief/effective_defaults.json')).json();
          const clone=structuredClone(defaults);clone.cards.typography.title_px=size;
          document.getElementById('visual').innerHTML=renderCard('C03',2,7.3,clone);
          const title=document.querySelector('#visual svg text');
          await document.fonts.ready;
          return {requested:size,text:title.textContent,attribute:title.getAttribute('font-size'),
            computed:getComputedStyle(title).fontSize};
        }""",size)
        path=QC/f"parameter_consumption_C03_title_{size}.png"
        page.screenshot(path=str(path),type="png")
        pngs.append(path)
        values.append(value)
    import numpy as np
    before=np.array(Image.open(pngs[0]).convert("RGB"))
    after=np.array(Image.open(pngs[1]).convert("RGB"))
    changed=int(np.count_nonzero(np.any(before!=after,axis=2)))
    page.evaluate("() => window.renderFrame(window.getCurrentFrame())")
    return {"passed":values[0]["computed"]=="72px" and values[1]["computed"]=="64px" and changed>100,
            "scope":"C03 cards.typography.title_px only, cloned in memory, not saved to defaults",
            "values":values,"changed_pixels":changed,
            "evidence":[{"path":str(p),"sha256":digest(p)} for p in pngs],
            "restored":"window.renderFrame(currentFrame) regenerated the actual scene after probe"}


def read_exact(stream,size):
    chunks=[]
    while size:
        block=stream.read(size)
        if not block:
            raise RuntimeError("FFmpeg抽帧输出提前结束")
        chunks.append(block)
        size-=len(block)
    return b"".join(chunks)


def decode_samples(config,video,frames,keep_frames,observations):
    import numpy as np
    from PIL import Image
    expression="select="+"+".join(f"eq(n\\,{frame})" for frame in frames)
    command=[str(config.ffmpeg),"-nostdin","-v","error","-i",str(video),"-map","0:v:0",
             "-vf",expression,"-fps_mode","passthrough","-pix_fmt","rgb24","-f","rawvideo","pipe:1"]
    evidence_dir=QC/"encoded_card_observations"
    evidence_dir.mkdir(parents=True,exist_ok=True)
    by_frame={item["frame"]:item for item in observations}
    kept={}
    log=QC/"output_sample_decode.log"
    with log.open("wb") as stderr:
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=stderr,creationflags=NO_WINDOW)
        try:
            for frame in frames:
                data=read_exact(process.stdout,config.width*config.height*3)
                array=np.frombuffer(data,dtype=np.uint8).reshape(config.height,config.width,3)
                if frame in keep_frames:
                    kept[frame]=array.copy()
                if frame in by_frame:
                    item=by_frame[frame]
                    path=evidence_dir/f"{item['card_id']}_frame_{frame:04d}.png"
                    Image.fromarray(array).save(path)
                    item["encoded_screenshot"]={"path":str(path),"sha256":digest(path)}
            require(not process.stdout.read(1),"抽帧数量超过采样计划")
            require(process.wait(timeout=180)==0,"FFmpeg采样解码失败")
        except BaseException:
            process.kill()
            process.wait(timeout=10)
            raise
        finally:
            process.stdout.close()
    return kept,{"command":command,"frames":frames,"count":len(frames),"log":str(log)}


def unmasked(config,states,frame_numbers):
    import numpy as np
    mask=np.ones((config.height,config.width),dtype=bool)
    rectangles=[]
    for frame in frame_numbers:
        rect=states[frame]["caption_rect"]
        if rect is None:
            continue
        x0=max(0,math.floor(rect["x"])-MASK_PADDING_PX)
        y0=max(0,math.floor(rect["y"])-MASK_PADDING_PX)
        x1=min(config.width,math.ceil(rect["x"]+rect["width"])+MASK_PADDING_PX)
        y1=min(config.height,math.ceil(rect["y"]+rect["height"])+MASK_PADDING_PX)
        mask[y0:y1,x0:x1]=False
        rectangles.append({"frame":frame,"actual_caption_plate_rect":rect,"comparison_mask_xyxy":[x0,y0,x1,y1]})
    require(float(mask.mean())>.9,"字幕屏蔽超过画面10%，拒绝扩大底部遮挡")
    return mask,rectangles


def image_metrics(a,b,mask):
    import numpy as np
    delta=a.astype(np.float32)-b.astype(np.float32)
    pixel=np.abs(delta).mean(axis=2)[mask]
    mse=float(np.mean((delta[mask])**2))
    return {"mean_absolute_rgb_error":float(pixel.mean()),
            "fraction_pixels_mean_error_over_12":float((pixel>12).mean()),
            "p99_mean_rgb_error":float(np.percentile(pixel,99)),
            "psnr_db":round(10*math.log10(255**2/mse),5) if mse else None}


def illustration_checks(config,illustrations,boundaries,states,references,decoded):
    import numpy as np
    results=[]
    for item in illustrations:
        clip,samples=item["clip"],item["frames"]
        pairs=[]
        for left,right in ((samples[0],samples[1]),(samples[1],samples[-1]),(samples[0],samples[-1])):
            mask,rects=unmasked(config,states,(left,right))
            metrics=image_metrics(decoded[left],decoded[right],mask)
            pairs.append({"frames":[left,right],"caption_masks":rects,"metrics":metrics,
                          "passed":metrics["mean_absolute_rgb_error"]<=2 and metrics["fraction_pixels_mean_error_over_12"]<=.003})
        fidelity=[]
        for frame in samples:
            mask,rects=unmasked(config,states,(samples[0],frame))
            reference=references[clip["id"]]
            metrics=image_metrics(reference,decoded[frame],mask)
            spatial_std=float(decoded[frame].mean(axis=2)[mask].std())
            reference_std=float(reference.mean(axis=2)[mask].std())
            fidelity.append({"frame":frame,"caption_masks":rects,"metrics_vs_decoded_loaded_source_page":metrics,
                             "spatial_luma_std":spatial_std,"reference_luma_std":reference_std,
                             "passed":metrics["mean_absolute_rgb_error"]<=6 and
                              (metrics["psnr_db"] is None or metrics["psnr_db"]>=27) and spatial_std>=10 and spatial_std>=reference_std*.7})
        results.append({"clip_id":clip["id"],"source":clip["asset_path"],"sampled_frames":samples,
                        "passed":all(p["passed"] for p in pairs+fidelity),"stillness_pairs":pairs,
                        "source_fidelity_and_nonblank":fidelity})
    edge_results=[]
    for left,right in boundaries:
        mask,rects=unmasked(config,states,(left,right))
        metrics=image_metrics(decoded[left],decoded[right],mask)
        edge_results.append({"frames":[left,right],"left_clip":states[left]["state"]["clip_id"],
                             "right_clip":states[right]["state"]["clip_id"],"caption_masks":rects,"metrics":metrics,
                             "passed":metrics["mean_absolute_rgb_error"]>1 and metrics["fraction_pixels_mean_error_over_12"]>.01})
    return {"passed":all(i["passed"] for i in results+edge_results),"scope":"sampled_first_middle_last_and_cut_adjacent_frames_only",
            "not_every_frame":True,"mask_basis":"actual DOM #caption background/border box per frame, not caption-safe band",
            "mask_padding_pixels":MASK_PADDING_PX,"mask_padding_reason":"small JPEG/H.264 edge/chroma tolerance",
            "thresholds":{"still_mean_absolute_rgb_error_max":2,"still_fraction_mean_pixel_error_over_12_max":.003,
                          "source_mean_absolute_rgb_error_max":6,"source_psnr_db_min":27,"nonblank_spatial_luma_std_min":10},
            "illustrations":results,"cut_edges":edge_results,
            "limits":"色彩编码误差有容差；有限采样不能证明每帧静止、无溶解或语义正确。I02与其余插画均包含源画面一致性和非空白检查。"}


def main():
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,"reconfigure"):
            stream.reconfigure(encoding="utf-8",errors="replace")
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video",required=True,help="本集内完整MP4路径；相对路径以本集为根")
    args=parser.parse_args()
    QC.mkdir(parents=True,exist_ok=True)
    report={"schema_version":1,"created_at":datetime.now(timezone.utc).isoformat(),"passed":False,
            "normal_speed_subjective_av":"not_performed","jianying_native_open":"not_performed",
            "scope":"full_decode_container_audio_waveform_and_sampled_visual_machine_checks","checks":{}}
    output=QC/"output_machine_checks.json"
    try:
        adapter=runpy.run_path(str(ROOT/"06_project/render.py"),run_name="episode_render_adapter_for_verification")
        config=adapter["load_config"]()
        video=adapter["inside_episode"](args.video)
        require(video.is_file() and video.suffix.lower()==".mp4" and not video.name.lower().endswith(".partial.mp4"),
                "--video必须是本集内已转正的完整MP4")
        scenes=read_json(ROOT/"03_storyboard/scenes.json")["scenes"]
        design=read_json(ROOT/"03_storyboard/semantic_design.json")
        bindings=binding_files(config,video,scenes)
        report.update({"episode_root":str(ROOT),"video":str(video),"stage":os.environ["V5_STAGE"],"bindings":bindings})
        print("检查容器与全片解码…",flush=True)
        report["checks"]["ffprobe"]=probe_video(config,video)
        report["checks"]["full_decode"]=full_decode(config,video)
        print("检查原音相关性与0偏移…",flush=True)
        report["checks"]["audio"]=audio_check(config,video)
        frames,illustrations,boundaries,observations=sampling_plan(config,scenes,design)
        print(f"采集实际字幕矩形与卡片状态：{len(frames)}个采样帧…",flush=True)
        states,references,browser,parameter_probe=collect_browser(config,adapter,frames,illustrations,observations)
        keep=set(f for item in illustrations for f in item["frames"])
        keep.update(f for pair in boundaries for f in pair)
        print("从成片提取观察帧并检查插画静止/源图一致性…",flush=True)
        decoded,decode_report=decode_samples(config,video,frames,keep,observations)
        report["sampled_frame_states"]={str(k):v for k,v in states.items()}
        report["browser"]=browser
        report["sample_decode"]=decode_report
        report["checks"]["illustration_sampled_checks"]=illustration_checks(config,illustrations,boundaries,states,references,decoded)
        report["checks"]["card_observations"]={"passed":not any(i["text_bounds_violations"] for i in observations),
              "scope":"declared_observation_frames_state_text_bounds_and_encoded_screenshots_only",
              "semantic_quality_acceptance":"not_established_by_machine_state_or_pixel_change","observations":observations}
        report["checks"]["parameter_consumption_probe"]=parameter_probe
        changed=[key for key,value in bindings.items() if digest(value["path"])!=value["sha256"]]
        report["checks"]["input_hash_stability"]={"passed":not changed,"changed":changed}
        report["passed"]=all(c["passed"] for c in report["checks"].values())
    except BaseException as exc:
        if isinstance(exc,(KeyboardInterrupt,SystemExit)):
            raise
        report["error"]=str(exc)
        report["traceback"]=traceback.format_exc()
        print("检查失败："+str(exc),file=sys.stderr)
    finally:
        partial=output.with_suffix(".partial.json")
        partial.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        os.replace(partial,output)
    print(f"机器检查{'通过' if report['passed'] else '未通过'}；报告：{output}",flush=True)
    return 0 if report["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())
