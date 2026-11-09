(()=>{"use strict";
const $=id=>document.getElementById(id), KEY="mytube-ai-studio-v3";
const tabs=["Overview","Script","Production Workflow","Characters & Pets","Story Bible","Scenes","Voices","Song Studio","Shorts","Smart Export","Watermark","AI Engine"];
let projects=load(),active=null,tab="Overview";
function load(){try{let raw=localStorage.getItem(KEY);if(!raw)raw=localStorage.getItem("mytube-projects-v2")||"[]";const x=JSON.parse(raw);if(!Array.isArray(x))return [];return x.map(p=>({...p,characters:Array.isArray(p.characters)?p.characters:[],scenes:Array.isArray(p.scenes)?p.scenes:[],shorts:Array.isArray(p.shorts)?p.shorts:[],voices:p.voices||{},song:typeof p.song==="object"&&p.song?p.song:{title:p.songTitle||"",mood:p.songMood||"Suspense",brief:"",lyrics:typeof p.song==="string"?p.song:""},export:p.export||{preset:"Balanced",resolution:"1080p",fps:"30",bitrate:8},watermark:typeof p.watermark==="object"&&p.watermark?p.watermark:{text:p.watermark||"",position:"Bottom right"},status:p.status||"Planning"}))}catch{return []}}
function persist(){try{localStorage.setItem(KEY,JSON.stringify(projects));return true}catch{toast("Storage is full. Export a backup and remove large text entries.");return false}}
function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function toast(s){$("toast").textContent=s;$("toast").classList.add("show");setTimeout(()=>$("toast").classList.remove("show"),2300)}
function makeProject(title,idea,format,type){return{id:crypto.randomUUID?crypto.randomUUID():String(Date.now()),title,idea,format,type,created:new Date().toISOString(),script:"",characters:[],bible:"",scenes:[],voices:{},song:{title:"",mood:"Suspense",brief:"",lyrics:""},shorts:[],export:{preset:"Balanced",resolution:"1080p",fps:"30",bitrate:8},watermark:{text:"",position:"Bottom right"},status:"Planning"}}
function renderProjects(){const live=projects.filter(p=>!p.deleted);$("projectList").innerHTML=live.length?live.map(p=>`<article class="project"><div><b>${esc(p.title)}</b><small>${esc(p.format)} · ${esc(p.status||"Planning")}</small></div><div class="project-actions"><button class="primary" data-open="${esc(p.id)}">Open</button><button class="danger" data-delete="${esc(p.id)}">Delete</button></div></article>`).join(""):'<div class="empty">No projects yet. Create your first drama above.</div>';
document.querySelectorAll("[data-open]").forEach(b=>b.onclick=()=>open(b.dataset.open));document.querySelectorAll("[data-delete]").forEach(b=>b.onclick=()=>{if(confirm("Delete this project? Export a backup first if you may need it.")){projects=projects.filter(p=>p.id!==b.dataset.delete);persist();renderProjects();toast("Project deleted.")}})}
$("createBtn").onclick=()=>{const title=$("newTitle").value.trim();if(!title){toast("Enter a drama title first.");return}const p=makeProject(title,$("newIdea").value.trim(),$("newFormat").value,$("newType").value);projects.unshift(p);persist();$("newTitle").value="";$("newIdea").value="";renderProjects();open(p.id);toast("Project created and saved.")};
function open(id){active=projects.find(p=>p.id===id);if(!active)return;tab="Overview";$("projectName").textContent=active.title;$("workspace").showModal();draw()}
$("closeWorkspace").onclick=()=>$("workspace").close();
function save(){persist();toast("Saved on this device.");}
function field(label,id,value="",placeholder="",type="text"){return `<label>${label}<input id="${id}" type="${type}" value="${esc(value)}" placeholder="${esc(placeholder)}"></label>`}
function area(label,id,value="",placeholder="",rows=4){return `<label>${label}<textarea id="${id}" rows="${rows}" placeholder="${esc(placeholder)}">${esc(value)}</textarea></label>`}
function btn(id,text,cls="primary"){return `<button id="${id}" class="${cls}">${text}</button>`}
function draw(){if(!active)return;const p=active;$("tabs").innerHTML=tabs.map(t=>`<button data-tab="${esc(t)}" class="${t===tab?"active":""}">${esc(t)}</button>`).join("");document.querySelectorAll("[data-tab]").forEach(b=>b.onclick=()=>{tab=b.dataset.tab;draw()});let h="";
if(tab==="Overview")h=`<h3>Project overview</h3><p>${esc(p.idea||"No story idea added yet.")}</p><div class="grid2"><div class="card"><b>${p.scenes.length}</b><p>Scenes planned</p></div><div class="card"><b>${p.characters.length}</b><p>Characters / pets</p></div><div class="card"><b>${p.shorts.length}</b><p>Shorts planned</p></div><div class="card"><b>${esc(p.status)}</b><p>Production status</p></div></div><div class="warning">Your project notes and settings save locally in this browser. Text generation and the production-pack workflow use the connected local model; optional media engines are shown in AI Engine status.</div>`;
if(tab==="Production Workflow")h=`<h3>AI production workflow</h3><p class="hint">Create a structured production pack from your saved script using the local text model. This prepares scene breakdowns, cast continuity, shot directions, Shorts concepts, audio cues and subtitle drafts; it does not generate image/video/audio files by itself.</p><div class="card">${btn("buildProduction","Generate production pack")}<p id="productionStatus" class="small">${p.productionPack?"A production pack is saved with this project.":"Requires a saved script and a running local text model."}</p>${p.productionPack?btn("queueMedia","Queue available scene video, dialogue and music jobs","secondary")+`<p id="mediaQueueStatus" class="small">Media generation requires configured providers in the private backend.</p>`:""}</div>${Array.isArray(p.mediaJobs)&&p.mediaJobs.length?`<div class="card"><h4>Latest media jobs</h4><p class="small">${p.mediaJobs.map(x=>`${esc(x.kind)}${x.sceneNumber?` · scene ${x.sceneNumber}`:""}: ${esc(x.status||"unknown")} (${Number(x.progress)||0}%)`).join(" · ")}</p>${btn("refreshMediaJobs","Refresh saved job status","secondary")}${p.mediaJobs.some(x=>x.status==="failed")?btn("retryMediaJobs","Retry failed jobs","secondary"):""}</div>`:""}${p.productionPack?`<div class="card"><h4>Production pack</h4><pre class="production-output">${esc(JSON.stringify(p.productionPack,null,2))}</pre></div>`:""}`;
if(tab==="Script")h=`<h3>Script Studio</h3><p class="hint">Generate an original first draft with your connected local text model, then edit and approve it here.</p><div class="card"><h3>AI script generator</h3>${area("What should happen in this drama?","scriptPrompt",p.idea||"Create an original drama opening with a strong hook, clear character motivations and cinematic dialogue.","Describe the story, episode, scene, tone and any must-keep facts...",5)}<div class="card-actions">${btn("generateScript","Generate script")}</div><p id="scriptGenStatus" class="small">Requires a reachable backend and a running local text model.</p></div>${area("Full script","script",p.script,"Generated or manually written scenes and dialogue...",12)}${btn("saveScript","Save script")}<div class="card"><h3>Creative Director</h3>${area("Revision instruction","revision","","e.g. Make the reveal more suspenseful, keep the character motivations consistent.",3)}${btn("copyRevision","Copy revision prompt","secondary")}</div>`;
if(tab==="Characters & Pets")h=`<h3>Create a character, pet or creature</h3>${field("Name","cname","","Character name")}<div class="two"><label>Type<select id="ctype">${["Human","Dog","Cat","Bird","Other pet","Fantasy creature"].map(x=>`<option>${x}</option>`).join("")}</select></label>${field("Story role","crole","","Lead, rival, companion...")}</div>${area("Appearance, wardrobe, personality and traits","cdesc","","Describe recognizable features, outfits and personality...",4)}${btn("addChar","Save character / pet")}<h3>Cast library</h3>${p.characters.map((c,i)=>`<div class="card"><b>${esc(c.name)}</b> · ${esc(c.type)}<p>${esc(c.role)} — ${esc(c.description)}</p><div class="card-actions"><button data-editchar="${i}" class="secondary">Edit</button><button data-delchar="${i}" class="danger">Delete</button></div></div>`).join("")||'<p class="empty">Your cast will appear here.</p>'}`;
if(tab==="Story Bible")h=`<h3>Story Bible & continuity</h3><p class="hint">Keep facts consistent across scenes and episodes.</p>${area("Characters, relationships, backstories, locations, timeline, rules and unresolved mysteries","bible",p.bible,"Record facts that must remain consistent...",12)}${btn("saveBible","Save Story Bible")}`;
if(tab==="Scenes")h=`<h3>Scene planner</h3>${field("Scene title","stitle","","Scene title")}<div class="two">${field("Location","slocation","","Where?")}<label>Camera<select id="scamera">${["Wide shot","Medium shot","Close-up","Over-the-shoulder","Tracking movement","Establishing shot"].map(x=>`<option>${x}</option>`).join("")}</select></label></div><div class="two"><label>Lighting<select id="slight">${["Natural","Soft","Low-key","Golden hour","Neon","Cinematic contrast"].map(x=>`<option>${x}</option>`).join("")}</select></label><label>Mood<select id="smood">${["Tense","Romantic","Mysterious","Joyful","Melancholic","Action","Hopeful"].map(x=>`<option>${x}</option>`).join("")}</select></label></div>${area("Action, dialogue and visual direction","sdesc","","What happens? Include blocking, emotion and sound...",4)}${btn("addScene","Add scene")}<h3>Scene list</h3>${p.scenes.map((s,i)=>`<div class="card"><b>${i+1}. ${esc(s.title)}</b><p>${esc(s.location)} · ${esc(s.camera)} · ${esc(s.lighting)} · ${esc(s.mood)}\n${esc(s.description)}</p><div class="card-actions"><button class="secondary" data-up="${i}">Move up</button><button class="secondary" data-down="${i}">Move down</button><button class="secondary" data-genimage="${i}">Generate scene image</button><button class="danger" data-delscene="${i}">Delete</button></div>${s.generatedImageAssetId?`<p class="small">Generated image saved · <a href="${(window.MYTUBE_API_BASE||window.location.origin).replace(/\/$/,"")}/api/assets/${encodeURIComponent(s.generatedImageAssetId)}" target="_blank" rel="noopener">Open image</a></p><img class="scene-preview" src="${(window.MYTUBE_API_BASE||window.location.origin).replace(/\/$/,"")}/api/assets/${encodeURIComponent(s.generatedImageAssetId)}" alt="Generated scene image" loading="lazy">`:""}</div>`).join("")||'<p class="empty">Add your first scene.</p>'}`;
if(tab==="Voices")h=`<h3>Voice direction</h3><p class="warning">Voice profiles are saved as direction only. Voice generation and audio editing require a connected service.</p>${p.characters.map((c,i)=>`<div class="card"><b>${esc(c.name)}</b><div class="two"><label>Voice style<select data-vstyle="${i}">${["Warm","Calm","Bright","Deep","Gentle","Playful","Mysterious","Narrator","Custom"].map(x=>`<option ${p.voices[i]?.style===x?"selected":""}>${x}</option>`).join("")}</select></label><label>Delivery<select data-vdelivery="${i}">${["Conversational","Dramatic","Whispered","Confident","Emotional","Neutral"].map(x=>`<option ${p.voices[i]?.delivery===x?"selected":""}>${x}</option>`).join("")}</select></label></div></div>`).join("")||'<p class="empty">Add characters before assigning voices.</p>'}${btn("saveVoices","Save voice directions")}`;
if(tab==="Song Studio")h=`<h3>Original music & song brief</h3><p class="warning">This stores your original music brief and lyrics; it does not create or play an audio track yet.</p>${field("Song title","songTitle",p.song.title,"Title")}<label>Mood<select id="songMood">${["Suspense","Sad","Romantic","Hopeful","Joyful","Mysterious","Triumphant","Playful"].map(x=>`<option ${p.song.mood===x?"selected":""}>${x}</option>`).join("")}</select></label>${area("Music direction","songBrief",p.song.brief,"Instruments, tempo feel, scene mood, vocals...",4)}${area("Original lyrics (optional)","songLyrics",p.song.lyrics,"Write your own lyrics...",6)}${btn("saveSong","Save song brief")}`;
if(tab==="Shorts")h=`<h3>Shorts planner</h3><p class="hint">Plan 5–10 promotional clips from your drama. Review each before using it.</p>${field("Short title","shortTitle","","Hook title")}${area("Clip concept","shortIdea","","Moment, hook, caption and ending...",3)}<label>Aspect ratio<select id="shortFormat"><option>Vertical 9:16</option><option>Square 1:1</option></select></label>${btn("addShort","Add Short idea")}<h3>Planned Shorts</h3>${p.shorts.map((s,i)=>`<div class="card"><b>${i+1}. ${esc(s.title)}</b><p>${esc(s.idea)} · ${esc(s.format)}</p><label>Source video clip<input id="shortFile${i}" type="file" accept="video/*"></label><div class="two"><label>Start time (seconds)<input id="shortStart${i}" type="number" min="0" step="0.1" value="0"></label><label>End time (seconds)<input id="shortEnd${i}" type="number" min="0.1" step="0.1" value="30"></label></div><label>Resolution<select id="shortRes${i}"><option>1080p</option><option>720p</option></select></label><button class="secondary" data-render-short="${i}">Render this Short (9:16)</button><p id="shortStatus${i}" class="small">${s.render?.status==="completed"?"Rendered Short is ready.":s.render?.status==="processing"?"Render is processing.":"Uses your uploaded clip; choose the time range."}</p>${s.render?.renderId?`<button class="secondary" data-refresh-short="${i}">Refresh render status</button>`:""}${s.render?.status==="completed"?`<a href="${esc(s.render.downloadUrl||"#")}" target="_blank" rel="noopener">Open rendered Short</a>`:""}<button class="danger" data-delshort="${i}">Delete</button></div>`).join("")||'<p class="empty">No Shorts planned yet.</p>'}`;
if(tab==="Smart Export")h=`<h3>Smart Export & Compression</h3><p class="hint">Export settings are prepared. The private backend includes an FFmpeg MP4 renderer; media assets must be uploaded to that backend before rendering.</p><div class="two"><label>Preset<select id="expPreset">${["High Quality","Balanced","Smaller File"].map(x=>`<option ${p.export.preset===x?"selected":""}>${x}</option>`).join("")}</select></label><label>Resolution<select id="expRes">${["720p","1080p","4K"].map(x=>`<option ${p.export.resolution===x?"selected":""}>${x}</option>`).join("")}</select></label></div><div class="two"><label>Output format<select id="expAspect"><option value="16:9">YouTube video · 16:9</option><option value="9:16">YouTube Shorts · 9:16</option></select></label><label>Frame rate<select id="expFps">${["24","25","30","60"].map(x=>`<option ${p.export.fps===x?"selected":""}>${x}</option>`).join("")}</select></label><label>Duration (minutes)<input id="expDuration" type="number" min="1" max="300" value="10"></label></div><p class="small">Illustrative estimate only, based on typical video bitrates. Actual size depends on footage, audio and encoder.</p><div id="sizeEstimate" class="estimate">—</div>${btn("saveExport","Save export settings")}<div class="card"><h3>Render your finished video</h3><p class="hint">Upload video clips in story order and an optional music/narration track. The backend will combine them into one MP4 using the settings above.</p><label>Video clips (select in playback order)<input id="renderClips" type="file" accept="video/*" multiple></label><label>Optional audio tracks (select multiple)<input id="renderAudio" type="file" accept="audio/*" multiple></label><div class="card-actions">${btn("renderUpload","Upload media and render MP4")}</div><p id="renderStatus" class="small">No render submitted.</p><a id="renderDownload" hidden download="mytube-export.mp4">Download finished MP4</a></div><div class="card"><h3>Subtitle drafts</h3><p>Export subtitle drafts from the production pack as editable text files.</p><div class="card-actions">${btn("subtitleEn","Download English subtitles","secondary")}${btn("subtitleZh","Download Chinese subtitles","secondary")}</div></div>`;
if(tab==="AI Engine")h=`<h3>AI Engine Connection</h3>
<p class="warning">Connect a private model backend here. This public website must never contain secret API keys.</p>
<div class="card"><h3>Automatic engine connection</h3><p id="engineStatus" class="small">Connecting to this studio's private engine…</p><button id="testEngine" class="secondary">Reconnect</button></div>
<div class="grid2"><div class="card"><b>Text / scripts</b><p id="capText">Checking…</p></div><div class="card"><b>Image generation</b><p id="capImage">Not connected</p></div><div class="card"><b>Video generation</b><p id="capVideo">Not connected</p></div><div class="card"><b>Voice generation</b><p id="capVoice">Not connected</p></div><div class="card"><b>Music generation</b><p id="capMusic">Not connected</p></div><div class="card"><b>MP4 rendering</b><p id="capRender">Checking FFmpeg…</p></div></div>
<div class="card"><h3>ComfyUI image workflow</h3><p class="hint">Paste an API-format workflow exported from ComfyUI once. MyTube uses it for scene image generation. The workflow must contain a positive CLIPTextEncode node; its node ID is entered below.</p>${area("ComfyUI API workflow JSON","imageWorkflowText",p.imageWorkflowText||"","Paste workflow JSON exported in API format…",5)}${field("Positive prompt node ID","imagePromptNode",p.imagePromptNode||"","e.g. 6")}${btn("saveImageWorkflow","Save image workflow")}</div>
<div class="warning">Self-hosting avoids third-party generation quotas, but hardware still limits speed and output. Phone-only generation of long cinematic video is not realistic.</div>`;
if(tab==="Watermark")h=`<h3>Watermark settings</h3><p class="warning">These settings are saved; the watermark is not burned into video until rendering is connected.</p>${field("Watermark text","wmText",p.watermark.text,"MyTube AI")}<label>Position<select id="wmPos">${["Bottom right","Bottom left","Top right","Top left","Center"].map(x=>`<option ${p.watermark.position===x?"selected":""}>${x}</option>`).join("")}</select></label>${btn("saveWM","Save watermark settings")}`;
$("workspaceContent").innerHTML=h;wire()}
function wire(){const p=active,click=(id,fn)=>{const e=$(id);if(e)e.onclick=()=>{fn();persist();draw();toast("Saved.")}};
click("saveScript",()=>p.script=$("script").value);
const buildProduction=$("buildProduction");
if(buildProduction)buildProduction.onclick=async()=>{
 const status=$("productionStatus"),base=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
 if(!p.script||!p.script.trim()){status.textContent="Save a script first in Script Studio.";return}
 buildProduction.disabled=true;status.textContent="Building production pack with local model…";
 try{
  const prompt="Return ONLY valid JSON, no markdown. Build a production pack for this original drama. JSON keys: logline, characters (array of {name, role, visual_continuity, voice_direction}), scenes (array of {number, slugline, action, visual_prompt, camera, lighting, audio_cues, dialogue_summary}), shorts (array of 5 objects {title, hook, excerpt_or_summary, vertical_visual_direction}), subtitle_draft_en (string), subtitle_draft_zh (string), production_notes (array). Do not invent copyrighted characters. Preserve exact story facts. Project: "+p.title+"\nStory Bible: "+(p.bible||"Not provided")+"\nCast: "+JSON.stringify(p.characters)+"\nSaved script:\n"+p.script;
  const cr=await fetch(base+"/api/jobs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({projectId:p.id,kind:"production",input:{prompt,system:"You are a film production coordinator. Output strict JSON only. Be concise but detailed enough to execute."}})});
  if(!cr.ok)throw Error("Backend rejected production job ("+cr.status+")");const job=await cr.json();
  for(let i=0;i<450;i++){await new Promise(r=>setTimeout(r,2000));const rr=await fetch(base+"/api/jobs/"+encodeURIComponent(job.jobId));if(!rr.ok)throw Error("Could not read job status");const j=await rr.json();status.textContent=(j.message||j.status)+" · "+(j.progress||0)+"%";if(j.status==="completed"){p.productionPack=j.output?.production||{production_notes:j.output?.text||""};if(Array.isArray(p.productionPack.shorts)&&p.productionPack.shorts.length){p.shorts=p.productionPack.shorts.slice(0,10).map((x,i)=>({title:x.title||`Short ${i+1}`,idea:x.hook||x.excerpt_or_summary||x.vertical_visual_direction||"",format:"Vertical 9:16",source:"production pack"}))}persist();status.textContent="Production pack generated and saved.";draw();return}if(j.status==="failed")throw Error(j.error||j.message)}
  throw Error("Production job is still running; its status is saved on the backend.");
 }catch(e){status.textContent="Production pack failed: "+e.message}finally{buildProduction.disabled=false}
};
const queueMedia=$("queueMedia");
if(queueMedia)queueMedia.onclick=async()=>{
 const status=$("mediaQueueStatus"),base=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
 const pack=p.productionPack||{},scenes=Array.isArray(pack.scenes)?pack.scenes:[];
 if(!scenes.length){status.textContent="No scenes in the production pack yet.";return}
 queueMedia.disabled=true;status.textContent="Submitting scene jobs…";
 try{
  const response=await fetch(base+"/api/production/queue",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({projectId:p.id,scenes,characters:pack.characters||p.characters||[],musicPrompt:pack.music_prompt||p.song?.brief||"",includeVideo:true,includeVoice:true,includeMusic:true})});
  if(!response.ok)throw Error("Queue request failed: "+(await response.text()).slice(0,300));
  const data=await response.json();let states={},rows=[];
  p.mediaJobIds=(data.jobs||[]).map(job=>job.jobId);p.mediaJobs=(data.jobs||[]).map(job=>({...job,status:"queued"}));persist();
  for(let cycle=0;cycle<90;cycle++){
   rows=await Promise.all(data.jobs.map(async job=>{
    let r=await fetch(base+"/api/jobs/"+encodeURIComponent(job.jobId));if(!r.ok)throw Error("Could not read job status");let current=await r.json();
    if(["submitted","processing","queued"].includes(current.status)){const refreshed=await fetch(base+"/api/jobs/"+encodeURIComponent(job.jobId)+"/refresh",{method:"POST"});if(refreshed.ok)current=await refreshed.json()}
    if(current.status==="completed" && ["video","voice","music"].includes(current.kind) && !current.output?.assetId){
     const imported=await fetch(base+"/api/jobs/"+encodeURIComponent(job.jobId)+"/import-output",{method:"POST"});
     if(imported.ok){const result=await imported.json();current.output={...(current.output||{}),assetId:result.assetId};current.message="Completed media imported: "+result.assetId}
     else if(imported.status!==409){const detail=await imported.text();current.message="Provider completed; media import pending: "+detail.slice(0,160)}
    }
    return current;
   }));
   states=rows.reduce((a,j)=>(a[j.status]=(a[j.status]||0)+1,a),{});
   p.mediaJobs=rows.map(j=>({jobId:j.jobId,kind:j.kind,sceneNumber:j.input?.sceneNumber,status:j.status,progress:j.progress,message:j.message,error:j.error,output:j.output}));persist();
   status.textContent=rows.map(j=>`${j.kind}${j.sceneNumber?" scene "+j.sceneNumber:""}: ${j.status} — ${j.message||j.error||""}`).join(" | ");
   if(rows.every(j=>["failed","completed"].includes(j.status)))break;
   await new Promise(r=>setTimeout(r,2000));
  }
  const failed=states.failed||0,completed=states.completed||0,submitted=states.submitted||0,processing=(states.processing||0)+(states.queued||0);
  status.textContent+=` · ${completed} completed, ${submitted} awaiting provider completion, ${processing} still running/queued, ${failed} failed. You can leave this screen; job IDs and last known status are saved in this project.`;
  const imported=rows.filter(j=>j.output?.assetId);
  if(imported.length){status.appendChild(document.createTextNode(" Files: "));imported.forEach((job,index)=>{if(index)status.appendChild(document.createTextNode(" · "));const a=document.createElement("a");a.href=base+"/api/assets/"+encodeURIComponent(job.output.assetId);a.target="_blank";a.rel="noopener";a.textContent=(job.kind+ (job.input?.sceneNumber?" scene "+job.input.sceneNumber:""));status.appendChild(a)})}
 }catch(e){status.textContent="Media queue: "+e.message}
 finally{queueMedia.disabled=false}
};
document.querySelectorAll("[data-refresh-short]").forEach(button=>button.onclick=async()=>{
 const i=Number(button.dataset.refreshShort),short=p.shorts[i],status=$("shortStatus"+i),base=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
 if(!short?.render?.renderId)return;
 button.disabled=true;status.textContent="Checking saved render…";
 try{
  const r=await fetch(base+"/api/render/"+encodeURIComponent(short.render.renderId),{cache:"no-store"});
  if(!r.ok)throw Error("Status request failed ("+r.status+")");
  const state=await r.json();short.render={...short.render,status:state.status,error:state.error||"",downloadUrl:state.status==="completed"?base+state.downloadUrl:short.render.downloadUrl};persist();
  status.textContent=state.status==="completed"?"Short rendered successfully.":state.status==="failed"?"Render failed: "+(state.error||"unknown error"):"Render is still processing.";
  draw();
 }catch(e){status.textContent="Could not refresh render: "+e.message}
 finally{button.disabled=false}
});
document.querySelectorAll("[data-render-short]").forEach(button=>button.onclick=async()=>{
 const i=Number(button.dataset.renderShort),short=p.shorts[i],status=$("shortStatus"+i),file=$("shortFile"+i)?.files?.[0];
 if(!file){status.textContent="Choose a source video clip first.";return}
 const start=Number($("shortStart"+i).value),end=Number($("shortEnd"+i).value);
 if(!Number.isFinite(start)||!Number.isFinite(end)||end<=start){status.textContent="End time must be greater than start time.";return}
 const base=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
 button.disabled=true;status.textContent="Uploading clip…";
 try{
  const fd=new FormData();fd.append("projectId",p.id);fd.append("file",file);
  const up=await fetch(base+"/api/assets",{method:"POST",body:fd});
  if(!up.ok)throw Error("Upload failed: "+(await up.text()).slice(0,180));
  const asset=await up.json();status.textContent="Starting vertical render…";
  const rr=await fetch(base+"/api/shorts/render",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({projectId:p.id,assetId:asset.assetId,startSeconds:start,endSeconds:end,resolution:$("shortRes"+i).value,watermark:p.watermark?.text||""})});
  if(!rr.ok)throw Error("Render request failed: "+(await rr.text()).slice(0,180));
  const job=await rr.json();short.render={renderId:job.renderId,status:"processing"};persist();
  for(let cycle=0;cycle<180;cycle++){
   await new Promise(r=>setTimeout(r,2000));
   const sr=await fetch(base+"/api/render/"+encodeURIComponent(job.renderId));
   if(!sr.ok)throw Error("Could not read render status");
   const state=await sr.json();
   if(state.status==="completed"){short.render={renderId:job.renderId,status:"completed",downloadUrl:base+state.downloadUrl};persist();status.textContent="Short rendered successfully.";draw();return}
   if(state.status==="failed")throw Error(state.error||"Short render failed");
   status.textContent="Rendering vertical Short…";
  }
  status.textContent="Render is still processing. Reopen this Short and check again later.";
 }catch(e){status.textContent="Short render failed: "+e.message}
 finally{button.disabled=false}
});
const refreshMediaJobs=$("refreshMediaJobs");
if(refreshMediaJobs)refreshMediaJobs.onclick=async()=>{
 refreshMediaJobs.disabled=true;
 try{
  const base=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
  const updated=await Promise.all((p.mediaJobs||[]).map(async job=>{
   const r=await fetch(base+"/api/jobs/"+encodeURIComponent(job.jobId));
   if(!r.ok)return job;
   let current=await r.json();
   if(["submitted","processing","queued"].includes(current.status)){
    const rr=await fetch(base+"/api/jobs/"+encodeURIComponent(job.jobId)+"/refresh",{method:"POST"});
    if(rr.ok)current=await rr.json();
   }
   return {...job,status:current.status,progress:current.progress,message:current.message,error:current.error,output:current.output};
  }));
  p.mediaJobs=updated;persist();draw();
 }catch(e){toast("Could not refresh jobs: "+e.message)}
 finally{refreshMediaJobs.disabled=false}
};
const retryMediaJobs=$("retryMediaJobs");
if(retryMediaJobs)retryMediaJobs.onclick=async()=>{
 retryMediaJobs.disabled=true;
 try{
  const base=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
  const failed=(p.mediaJobs||[]).filter(job=>job.status==="failed");
  const retried=await Promise.all(failed.map(async job=>{
   const r=await fetch(base+"/api/jobs/"+encodeURIComponent(job.jobId)+"/retry",{method:"POST"});
   if(!r.ok)throw Error("Retry failed: "+(await r.text()).slice(0,180));
   return await r.json();
  }));
  const byOld=new Map(retried.map((job,i)=>[failed[i].jobId,job]));
  p.mediaJobs=(p.mediaJobs||[]).map(job=>byOld.has(job.jobId)?{jobId:byOld.get(job.jobId).jobId,kind:job.kind,sceneNumber:job.sceneNumber,status:"queued",progress:0,message:"Retry queued"}:job);
  p.mediaJobIds=p.mediaJobs.map(job=>job.jobId);persist();draw();
 }catch(e){toast(e.message)}
 finally{retryMediaJobs.disabled=false}
};
const genScript=$("generateScript");
if(genScript)genScript.onclick=async()=>{
  const status=$("scriptGenStatus"),base=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
  const prompt=$("scriptPrompt").value.trim();
  
  if(!prompt){status.textContent="Describe the story first.";return}
  genScript.disabled=true;status.textContent="Submitting script job…";
  try{
    const created=await fetch(base+"/api/jobs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({projectId:p.id,kind:"text",input:{prompt:"Write a complete original drama script draft for project: "+p.title+". Project idea: "+p.idea+". User direction: "+prompt+". Include a compelling opening, scene headings, action and dialogue. Preserve originality and internal continuity."},output:{}})});
    if(!created.ok)throw new Error("Backend rejected the job ("+created.status+").");
    const job=await created.json();status.textContent="Job queued…";
    for(let i=0;i<450;i++){
      await new Promise(r=>setTimeout(r,2000));
      const rr=await fetch(base+"/api/jobs/"+encodeURIComponent(job.jobId));
      if(!rr.ok)throw new Error("Could not read job status ("+rr.status+").");
      const current=await rr.json();
      status.textContent=(current.message||current.status)+" "+(current.progress||0)+"%";
      if(current.status==="completed"){
        const generated=current.output?.text||"";
        if(!generated)throw new Error("Job completed without script text.");
        p.script=generated;persist();$("script").value=generated;status.textContent="Script generated and saved. Review and edit it before approval.";toast("AI script draft generated.");break;
      }
      if(current.status==="failed")throw new Error(current.error||current.message||"Generation failed.");
      if(i===449)throw new Error("This job is taking longer than expected. Its status remains saved on the backend.");
    }
  }catch(e){status.textContent="Script generation failed: "+e.message}
  finally{genScript.disabled=false}
};
click("saveBible",()=>p.bible=$("bible").value);
click("addChar",()=>{let name=$("cname").value.trim();if(!name){toast("Enter a character name.");return}p.characters.push({name,type:$("ctype").value,role:$("crole").value,description:$("cdesc").value});});
click("addScene",()=>{let title=$("stitle").value.trim();if(!title){toast("Enter a scene title.");return}p.scenes.push({title,location:$("slocation").value,camera:$("scamera").value,lighting:$("slight").value,mood:$("smood").value,description:$("sdesc").value})});
click("saveSong",()=>p.song={title:$("songTitle").value,mood:$("songMood").value,brief:$("songBrief").value,lyrics:$("songLyrics").value});
click("addShort",()=>{let title=$("shortTitle").value.trim();if(!title){toast("Enter a Short title.");return}p.shorts.push({title,idea:$("shortIdea").value,format:$("shortFormat").value})});
click("saveWM",()=>p.watermark={text:$("wmText").value,position:$("wmPos").value});
click("saveExport",()=>p.export={preset:$("expPreset").value,resolution:$("expRes").value,fps:$("expFps").value,bitrate:bitrate($("expPreset").value)});
const apiBase=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
function downloadText(name,text){const blob=new Blob([text||""],{type:"text/plain;charset=utf-8"}),url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500)}
const enBtn=$("subtitleEn"),zhBtn=$("subtitleZh");
if(enBtn)enBtn.onclick=()=>downloadText((p.title||"drama").replace(/[^a-z0-9_-]/gi,"_")+"-en-subtitles.txt",p.productionPack?.subtitle_draft_en||"Generate a production pack first to create the English subtitle draft.");
if(zhBtn)zhBtn.onclick=()=>downloadText((p.title||"drama").replace(/[^a-z0-9_-]/gi,"_")+"-zh-subtitles.txt",p.productionPack?.subtitle_draft_zh||"Generate a production pack first to create the Chinese subtitle draft.");
const renderBtn=$("renderUpload");
if(renderBtn)renderBtn.onclick=async()=>{
 const status=$("renderStatus"),link=$("renderDownload"),clips=[...($("renderClips")?.files||[])],audios=[...($("renderAudio")?.files||[])];
 if(!clips.length){status.textContent="Choose at least one video clip.";return}
 renderBtn.disabled=true;link.hidden=true;
 try{
  const clipIds=[];
  for(let i=0;i<clips.length;i++){
   status.textContent=`Uploading video ${i+1} of ${clips.length}…`;
   const fd=new FormData();fd.append("projectId",p.id);fd.append("file",clips[i]);
   const r=await fetch(apiBase+"/api/assets",{method:"POST",body:fd});if(!r.ok)throw Error("Video upload failed: "+(await r.text()).slice(0,240));clipIds.push((await r.json()).assetId);
  }
  const audioIds=[];for(let i=0;i<audios.length;i++){status.textContent=`Uploading audio ${i+1} of ${audios.length}…`;const fd=new FormData();fd.append("projectId",p.id);fd.append("file",audios[i]);const r=await fetch(apiBase+"/api/assets",{method:"POST",body:fd});if(!r.ok)throw Error("Audio upload failed: "+(await r.text()).slice(0,240));audioIds.push((await r.json()).assetId)}
  status.textContent="Starting MP4 render…";
  const r=await fetch(apiBase+"/api/render",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({projectId:p.id,clips:clipIds,audioTracks:audioIds,resolution:$("expRes").value,fps:Number($("expFps").value),preset:$("expPreset").value,watermark:p.watermark?.text||"",watermarkPosition:p.watermark?.position||"Bottom right",aspectRatio:$("expAspect")?.value||"16:9"})});
  if(!r.ok)throw Error("Render request failed: "+(await r.text()).slice(0,240));const job=await r.json();
  for(let i=0;i<720;i++){await new Promise(resolve=>setTimeout(resolve,3000));const sr=await fetch(apiBase+"/api/render/"+encodeURIComponent(job.renderId));if(!sr.ok)throw Error("Could not read render status.");const state=await sr.json();status.textContent=state.status==="processing"?`Rendering MP4… (${Math.min(99,Math.round((i+1)/720*100))}% time indicator)`:state.status==="completed"?"MP4 render complete.":"Render failed: "+(state.error||"Unknown error");if(state.status==="completed"){link.href=apiBase+state.downloadUrl;link.hidden=false;return}if(state.status==="failed")throw Error(state.error||"FFmpeg render failed")}
  status.textContent="Render is still processing on the backend. Reopen Smart Export to check again.";
 }catch(e){status.textContent="Export failed: "+e.message}finally{renderBtn.disabled=false}
};

click("saveImageWorkflow",()=>{
 const raw=$("imageWorkflowText").value.trim(),node=$("imagePromptNode").value.trim();
 let parsed;try{parsed=JSON.parse(raw)}catch{toast("Workflow JSON is invalid.");return}
 if(!parsed||typeof parsed!=="object"||Array.isArray(parsed)){toast("Workflow must be a JSON object.");return}
 if(!node||!parsed[node]||!parsed[node].inputs||!("text" in parsed[node].inputs)){toast("That node ID must point to a node with an inputs.text field.");return}
 p.imageWorkflowText=raw;p.imagePromptNode=node;
});
document.querySelectorAll("[data-genimage]").forEach(button=>button.onclick=async()=>{
 const index=Number(button.dataset.genimage),scene=p.scenes[index],base=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
 const status=document.createElement("p");status.className="small";button.parentElement.parentElement.appendChild(status);
 if(!p.imageWorkflowText||!p.imagePromptNode){status.textContent="First save a ComfyUI API workflow in AI Engine.";return}
 let workflow;try{workflow=JSON.parse(p.imageWorkflowText)}catch{status.textContent="Saved workflow JSON is invalid.";return}
 const characterNotes=(p.characters||[]).map(c=>`${c.name}: ${c.description||c.role||""}`).join("\n");
 const prompt=[`Cinematic original drama scene: ${scene.title}.`,`Location: ${scene.location||"as described"}.`,`Camera: ${scene.camera||"cinematic framing"}.`,`Lighting: ${scene.lighting||"cinematic"}.`,`Mood: ${scene.mood||"dramatic"}.`,`Action and visual direction: ${scene.description||""}.`,`Character continuity reference: ${characterNotes}.`,`Story continuity: ${p.bible||""}.`,`Maintain the same character appearance and wardrobe as their established descriptions. Create one coherent film still, no captions, no logos.`].join("\n");
 workflow[p.imagePromptNode].inputs.text=prompt;
 button.disabled=true;status.textContent="Submitting image generation…";
 try{
  const response=await fetch(base+"/api/engines/image",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt,workflow})});
  if(!response.ok)throw Error((await response.text()).slice(0,350));
  const submitted=await response.json();if(!submitted.promptId)throw Error("ComfyUI did not return a prompt ID.");
  let result=null;
  for(let attempt=0;attempt<180;attempt++){
   await new Promise(resolve=>setTimeout(resolve,2000));
   const poll=await fetch(base+"/api/engines/image/"+encodeURIComponent(submitted.promptId));
   if(!poll.ok)throw Error("Image status check failed: "+(await poll.text()).slice(0,200));
   result=await poll.json();status.textContent="Image generation: "+result.status;
   if(result.status==="completed")break;
  }
  if(result?.status!=="completed")throw Error("Image generation is still running; retry status from ComfyUI history.");
  if(!result.outputs?.length)throw Error("ComfyUI completed but returned no image outputs.");
  const imageResponse=await fetch(base+"/api/engines/image/"+encodeURIComponent(submitted.promptId)+"/output/0");
  if(!imageResponse.ok)throw Error("Could not retrieve generated image.");
  const blob=await imageResponse.blob(),fd=new FormData();
  fd.append("projectId",p.id);fd.append("file",new File([blob],`scene-${index+1}.png`,{type:blob.type||"image/png"}));
  const saved=await fetch(base+"/api/assets",{method:"POST",body:fd});
  if(!saved.ok)throw Error("Image generated but asset save failed: "+(await saved.text()).slice(0,200));
  const asset=await saved.json();scene.generatedImageAssetId=asset.assetId;persist();
  status.textContent="Scene image generated and saved to project.";draw();
 }catch(error){status.textContent="Image generation failed: "+error.message}
 finally{button.disabled=false}
});
click("saveVoices",()=>{document.querySelectorAll("[data-vstyle]").forEach(e=>{let i=e.dataset.vstyle;p.voices[i]={...(p.voices[i]||{}),style:e.value}});document.querySelectorAll("[data-vdelivery]").forEach(e=>{let i=e.dataset.vdelivery;p.voices[i]={...(p.voices[i]||{}),delivery:e.value}})});
const revision=$("copyRevision");if(revision)revision.onclick=()=>copy(`Creative Director revision request for "${p.title}":\n${$("revision").value}\nPreserve established character identities, relationships, timeline and Story Bible facts. Return only the revised material and explain continuity changes.`);
const estimate=()=>{let d=Math.max(1,Number($("expDuration")?.value)||10),r=$("expRes")?.value||p.export.resolution,pr=$("expPreset")?.value||p.export.preset;let b=pr==="High Quality"?({"720p":5,"1080p":12,"4K":45}[r]):pr==="Smaller File"?({"720p":1.5,"1080p":3,"4K":12}[r]):({"720p":3,"1080p":8,"4K":25}[r]);let mb=(b*60*d)/8+0.128*60*d/8;$("sizeEstimate").textContent=`Estimated ${mb>=1024?(mb/1024).toFixed(2)+" GB":Math.round(mb)+" MB"}`};
["expDuration","expRes","expPreset"].forEach(id=>{if($(id))$(id).onchange=estimate});if($("sizeEstimate"))estimate();
document.querySelectorAll("[data-delchar]").forEach(b=>b.onclick=()=>{p.characters.splice(+b.dataset.delchar,1);persist();draw()});
document.querySelectorAll("[data-editchar]").forEach(b=>b.onclick=()=>{let c=p.characters[+b.dataset.editchar],n=prompt("Character name",c.name);if(n!==null){c.name=n.trim()||c.name;persist();draw()}});
document.querySelectorAll("[data-delscene]").forEach(b=>b.onclick=()=>{p.scenes.splice(+b.dataset.delscene,1);persist();draw()});
document.querySelectorAll("[data-delshort]").forEach(b=>b.onclick=()=>{p.shorts.splice(+b.dataset.delshort,1);persist();draw()});
document.querySelectorAll("[data-up]").forEach(b=>b.onclick=()=>{let i=+b.dataset.up;if(i){[p.scenes[i-1],p.scenes[i]]=[p.scenes[i],p.scenes[i-1]];persist();draw()}});
const engineStatus=$("engineStatus");
async function checkEngine(){if(!engineStatus)return;engineStatus.textContent="Connecting…";try{const r=await fetch(location.origin+"/health",{cache:"no-store"});if(!r.ok)throw Error();const d=await r.json();const a=d.adapters||{},t=a.text;engineStatus.textContent=d.status==="ok"?"Backend online · capability status below.":"Engine responded but is not ready.";const put=(id,value)=>{const el=$(id);if(el)el.textContent=value};put("capText",t?.installed?"Ready · "+t.model:"Backend online; local model unavailable");put("capImage",a.image?.configured?"Endpoint configured; adapter verification pending":"No image engine connected");put("capVideo",a.video?.configured?"Endpoint configured; adapter verification pending":"No video engine connected");put("capVoice",a.voice?.configured?"Endpoint configured; adapter verification pending":"No voice engine connected");put("capMusic",a.music?.configured?"Endpoint configured; adapter verification pending":"No music engine connected");put("capRender",a.render?.available?"FFmpeg renderer available":"FFmpeg not installed")}catch{engineStatus.textContent="Engine offline. Reopen this studio when its Codespace is running."}}
if($("testEngine"))$("testEngine").onclick=checkEngine;
checkEngine();document.addEventListener("visibilitychange",()=>{if(!document.hidden)checkEngine()});
document.querySelectorAll("[data-down]").forEach(b=>b.onclick=()=>{let i=+b.dataset.down;if(i<p.scenes.length-1){[p.scenes[i+1],p.scenes[i]]=[p.scenes[i],p.scenes[i+1]];persist();draw()}});
}
async function copy(s){try{await navigator.clipboard.writeText(s);toast("Copied.")}catch{toast("Clipboard unavailable in this browser.")}}
$("backupBtn").onclick=()=>{const blob=new Blob([JSON.stringify({app:"MyTube AI",version:3,projects},null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="mytube-ai-backup.json";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
$("restoreFile").onchange=async e=>{const f=e.target.files?.[0];if(!f)return;try{const d=JSON.parse(await f.text());if(d.app!=="MyTube AI"||!Array.isArray(d.projects))throw Error();if(!confirm("Restore backup? This replaces the projects currently stored in this browser."))return;projects=d.projects;persist();renderProjects();toast("Backup restored.");}catch{toast("Backup file could not be read.")}e.target.value=""};
$("themeBtn").onclick=()=>document.body.classList.toggle("light");
renderProjects();
})();