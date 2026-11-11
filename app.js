(()=>{"use strict";
const $=id=>document.getElementById(id), KEY="mytube-ai-studio-v3";
const tabs=["Overview","Script","Characters & Pets","Story Bible","Scenes","Voices","Song Studio","Media Lab","Shorts","Smart Export","Watermark","AI Engine"];
let projects=load(),active=null,tab="Overview";
function load(){try{let raw=localStorage.getItem(KEY);if(!raw)raw=localStorage.getItem("mytube-projects-v2")||"[]";const x=JSON.parse(raw);if(!Array.isArray(x))return [];return x.map(p=>({...p,characters:Array.isArray(p.characters)?p.characters:[],scenes:Array.isArray(p.scenes)?p.scenes:[],shorts:Array.isArray(p.shorts)?p.shorts:[],media:p.media||{images:[],video:null,music:null,export:null},voices:p.voices||{},song:typeof p.song==="object"&&p.song?p.song:{title:p.songTitle||"",mood:p.songMood||"Suspense",brief:"",lyrics:typeof p.song==="string"?p.song:""},export:p.export||{preset:"Balanced",resolution:"1080p",fps:"30",bitrate:8},watermark:typeof p.watermark==="object"&&p.watermark?p.watermark:{text:p.watermark||"",position:"Bottom right"},status:p.status||"Planning"}))}catch{return []}}
function persist(){try{localStorage.setItem(KEY,JSON.stringify(projects));return true}catch{toast("Storage is full. Export a backup and remove large text entries.");return false}}
function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function toast(s){$("toast").textContent=s;$("toast").classList.add("show");setTimeout(()=>$("toast").classList.remove("show"),2300)}
function makeProject(title,idea,format,type){return{id:crypto.randomUUID?crypto.randomUUID():String(Date.now()),title,idea,format,type,created:new Date().toISOString(),script:"",characters:[],bible:"",scenes:[],voices:{},song:{title:"",mood:"Suspense",brief:"",lyrics:""},shorts:[],media:{images:[],video:null,music:null,export:null},export:{preset:"Balanced",resolution:"1080p",fps:"30",bitrate:8},watermark:{text:"",position:"Bottom right"},status:"Planning"}}
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
if(tab==="Overview")h=`<h3>Project overview</h3><p>${esc(p.idea||"No story idea added yet.")}</p><div class="grid2"><div class="card"><b>${p.scenes.length}</b><p>Scenes planned</p></div><div class="card"><b>${p.characters.length}</b><p>Characters / pets</p></div><div class="card"><b>${p.shorts.length}</b><p>Shorts planned</p></div><div class="card"><b>${esc(p.status)}</b><p>Production status</p></div></div><div class="warning">This is a planning workspace. Generation buttons are not connected to an AI media provider yet. Your project notes and settings save locally in this browser.</div>`;
if(tab==="Script")h=`<h3>Script Studio</h3><p class="hint">Generate an original first draft with your connected local text model, then edit and approve it here.</p><div class="card"><h3>AI script generator</h3>${area("What should happen in this drama?","scriptPrompt",p.idea||"Create an original drama opening with a strong hook, clear character motivations and cinematic dialogue.","Describe the story, episode, scene, tone and any must-keep facts...",5)}<div class="card-actions">${btn("generateScript","Generate script")}</div><p id="scriptGenStatus" class="small">Requires a reachable backend and a running local text model.</p></div>${area("Full script","script",p.script,"Generated or manually written scenes and dialogue...",12)}${btn("saveScript","Save script")}<div class="card"><h3>Creative Director</h3>${area("Revision instruction","revision","","e.g. Make the reveal more suspenseful, keep the character motivations consistent.",3)}${btn("copyRevision","Copy revision prompt","secondary")}</div>`;
if(tab==="Characters & Pets")h=`<h3>Create a character, pet or creature</h3>${field("Name","cname","","Character name")}<div class="two"><label>Type<select id="ctype">${["Human","Dog","Cat","Bird","Other pet","Fantasy creature"].map(x=>`<option>${x}</option>`).join("")}</select></label>${field("Story role","crole","","Lead, rival, companion...")}</div>${area("Appearance, wardrobe, personality and traits","cdesc","","Describe recognizable features, outfits and personality...",4)}${btn("addChar","Save character / pet")}<h3>Cast library</h3>${p.characters.map((c,i)=>`<div class="card"><b>${esc(c.name)}</b> · ${esc(c.type)}<p>${esc(c.role)} — ${esc(c.description)}</p><div class="card-actions"><button data-editchar="${i}" class="secondary">Edit</button><button data-delchar="${i}" class="danger">Delete</button></div></div>`).join("")||'<p class="empty">Your cast will appear here.</p>'}`;
if(tab==="Story Bible")h=`<h3>Story Bible & continuity</h3><p class="hint">Keep facts consistent across scenes and episodes.</p>${area("Characters, relationships, backstories, locations, timeline, rules and unresolved mysteries","bible",p.bible,"Record facts that must remain consistent...",12)}${btn("saveBible","Save Story Bible")}`;
if(tab==="Scenes")h=`<h3>Scene planner</h3>${field("Scene title","stitle","","Scene title")}<div class="two">${field("Location","slocation","","Where?")}<label>Camera<select id="scamera">${["Wide shot","Medium shot","Close-up","Over-the-shoulder","Tracking movement","Establishing shot"].map(x=>`<option>${x}</option>`).join("")}</select></label></div><div class="two"><label>Lighting<select id="slight">${["Natural","Soft","Low-key","Golden hour","Neon","Cinematic contrast"].map(x=>`<option>${x}</option>`).join("")}</select></label><label>Mood<select id="smood">${["Tense","Romantic","Mysterious","Joyful","Melancholic","Action","Hopeful"].map(x=>`<option>${x}</option>`).join("")}</select></label></div>${area("Action, dialogue and visual direction","sdesc","","What happens? Include blocking, emotion and sound...",4)}${btn("addScene","Add scene")}<h3>Scene list</h3>${p.scenes.map((s,i)=>`<div class="card"><b>${i+1}. ${esc(s.title)}</b><p>${esc(s.location)} · ${esc(s.camera)} · ${esc(s.lighting)} · ${esc(s.mood)}\n${esc(s.description)}</p><div class="card-actions"><button class="secondary" data-up="${i}">Move up</button><button class="secondary" data-down="${i}">Move down</button><button class="danger" data-delscene="${i}">Delete</button></div></div>`).join("")||'<p class="empty">Add your first scene.</p>'}`;
if(tab==="Voices")h=`<h3>Voice direction</h3><p class="hint">Generate a local speech preview when the backend has eSpeak installed. This is a synthetic preview voice, not a cloned character voice.</p><div class="card"><h3>Dialogue preview</h3>${area("Text to speak","voiceText","","Enter a short line of dialogue...",4)}<div class="card-actions">${btn("generateVoice","Generate voice preview")}</div><p id="voiceStatus" class="small">Requires the backend speech engine to be installed.</p><audio id="voicePlayer" controls style="display:none;width:100%;margin-top:12px"></audio></div>${p.characters.map((c,i)=>`<div class="card"><b>${esc(c.name)}</b><div class="two"><label>Voice style<select data-vstyle="${i}">${["Warm","Calm","Bright","Deep","Gentle","Playful","Mysterious","Narrator","Custom"].map(x=>`<option ${p.voices[i]?.style===x?"selected":""}>${x}</option>`).join("")}</select></label><label>Delivery<select data-vdelivery="${i}">${["Conversational","Dramatic","Whispered","Confident","Emotional","Neutral"].map(x=>`<option ${p.voices[i]?.delivery===x?"selected":""}>${x}</option>`).join("")}</select></label></div></div>`).join("")||'<p class="empty">Add characters before assigning voices.</p>'}${btn("saveVoices","Save voice directions")}`;
if(tab==="Media Lab")h=`<h3>Media production lab</h3><p class="hint">Generate assets with the connected backend. Image generation needs a Stable Diffusion WebUI-compatible API; video and MP4 export use FFmpeg. Music is synthesized locally by the backend.</p>
<div class="card"><h3>1 · Generate an image</h3>${area("Image prompt","mediaImagePrompt","", "Describe the scene, characters, setting, lighting and visual style...",4)}<div class="two"><label>Width<select id="mediaImageWidth"><option value="768">768</option><option value="512">512</option><option value="1024">1024</option></select></label><label>Height<select id="mediaImageHeight"><option value="512">512</option><option value="768">768</option><option value="1024">1024</option></select></label></div>${btn("makeImage","Generate image")}<p id="imageJobStatus" class="small"></p><div id="imageGallery" class="media-gallery">${(p.media.images||[]).map((x,i)=>`<div class="card"><img src="${esc(x.url)}" alt="Generated scene image" style="width:100%;border-radius:10px"><label><input type="checkbox" data-media-image="${i}" checked> Include in video</label></div>`).join("")||"No generated images yet."}</div></div>
<div class="card"><h3>2 · Create a video from images</h3><p>Choose generated images above. FFmpeg assembles them into a 720p MP4 sequence.</p><label>Seconds per image<input id="mediaSeconds" type="number" min="2" max="30" value="4"></label>${btn("makeVideo","Create video")}<p id="videoJobStatus" class="small"></p>${p.media.video?`<video controls playsinline src="${esc(p.media.video.url)}" style="width:100%"></video>`:""}</div>
<div class="card"><h3>3 · Generate original background music</h3><div class="two"><label>Mood<select id="mediaMusicMood">${["Suspense","Sad","Romantic","Hopeful","Joyful","Mysterious","Triumphant","Playful"].map(x=>`<option>${x}</option>`).join("")}</select></label><label>Duration (seconds)<input id="mediaMusicDuration" type="number" min="5" max="180" value="30"></label></div>${btn("makeMusic","Compose music")}<p id="musicJobStatus" class="small"></p>${p.media.music?`<audio controls src="${esc(p.media.music.url)}" style="width:100%"></audio>`:""}</div>
<div class="card"><h3>4 · Export final MP4</h3><p>Combine the generated video with your generated music into one MP4 file.</p>${btn("makeExport","Render final MP4")}<p id="exportJobStatus" class="small"></p>${p.media.export?`<a class="primary" href="${esc(p.media.export.url)}" download>Download final MP4</a>`:""}</div>`;
if(tab==="Song Studio")h=`<h3>Original music & song brief</h3><p class="warning">This stores your original music brief and lyrics; it does not create or play an audio track yet.</p>${field("Song title","songTitle",p.song.title,"Title")}<label>Mood<select id="songMood">${["Suspense","Sad","Romantic","Hopeful","Joyful","Mysterious","Triumphant","Playful"].map(x=>`<option ${p.song.mood===x?"selected":""}>${x}</option>`).join("")}</select></label>${area("Music direction","songBrief",p.song.brief,"Instruments, tempo feel, scene mood, vocals...",4)}${area("Original lyrics (optional)","songLyrics",p.song.lyrics,"Write your own lyrics...",6)}${btn("saveSong","Save song brief")}`;
if(tab==="Shorts")h=`<h3>Shorts planner</h3><p class="hint">Plan 5–10 promotional clips from your drama. Review each before using it.</p>${field("Short title","shortTitle","","Hook title")}${area("Clip concept","shortIdea","","Moment, hook, caption and ending...",3)}<label>Aspect ratio<select id="shortFormat"><option>Vertical 9:16</option><option>Square 1:1</option></select></label>${btn("addShort","Add Short idea")}<h3>Planned Shorts</h3>${p.shorts.map((s,i)=>`<div class="card"><b>${i+1}. ${esc(s.title)}</b><p>${esc(s.idea)} · ${esc(s.format)}</p><button class="danger" data-delshort="${i}">Delete</button></div>`).join("")||'<p class="empty">No Shorts planned yet.</p>'}`;
if(tab==="Smart Export")h=`<h3>Smart Export & Compression</h3><p class="warning">Export settings are prepared, but this version has no video-rendering or compression engine connected. It cannot yet render or combine separate tracks into a finished MP4.</p><div class="two"><label>Preset<select id="expPreset">${["High Quality","Balanced","Smaller File"].map(x=>`<option ${p.export.preset===x?"selected":""}>${x}</option>`).join("")}</select></label><label>Resolution<select id="expRes">${["720p","1080p","4K"].map(x=>`<option ${p.export.resolution===x?"selected":""}>${x}</option>`).join("")}</select></label></div><div class="two"><label>Frame rate<select id="expFps">${["24","25","30","60"].map(x=>`<option ${p.export.fps===x?"selected":""}>${x}</option>`).join("")}</select></label><label>Duration (minutes)<input id="expDuration" type="number" min="1" max="300" value="10"></label></div><p class="small">Illustrative estimate only, based on typical video bitrates. Actual size depends on footage, audio and encoder.</p><div id="sizeEstimate" class="estimate">—</div>${btn("saveExport","Save export settings")}<div class="card"><h3>One complete download</h3><p>Target output: one MP4 containing synchronized video and audio, not separate downloads. This becomes available when the rendering/export engine is integrated.</p></div>`;
if(tab==="AI Engine")h=`<h3>AI Engine Connection</h3>
<p class="warning">Connect a private model backend here. This public website must never contain secret API keys.</p>
<div class="card"><h3>Automatic engine connection</h3><p id="engineStatus" class="small">Connecting to this studio's private engine…</p><button id="testEngine" class="secondary">Reconnect</button></div>
<div class="grid2"><div class="card"><b>Text / scripts</b><p id="capText">Checking…</p></div><div class="card"><b>Image generation</b><p id="capImage">Not connected</p></div><div class="card"><b>Video generation</b><p id="capVideo">Not connected</p></div><div class="card"><b>Voice generation</b><p id="capVoice">Not connected</p></div><div class="card"><b>Music generation</b><p id="capMusic">Not connected</p></div><div class="card"><b>MP4 rendering</b><p id="capRender">Checking FFmpeg…</p></div></div>
<div class="warning">Self-hosting avoids third-party generation quotas, but hardware still limits speed and output. Phone-only generation of long cinematic video is not realistic.</div>`;
if(tab==="Watermark")h=`<h3>Watermark settings</h3><p class="warning">These settings are saved; the watermark is not burned into video until rendering is connected.</p>${field("Watermark text","wmText",p.watermark.text,"MyTube AI")}<label>Position<select id="wmPos">${["Bottom right","Bottom left","Top right","Top left","Center"].map(x=>`<option ${p.watermark.position===x?"selected":""}>${x}</option>`).join("")}</select></label>${btn("saveWM","Save watermark settings")}`;
$("workspaceContent").innerHTML=h;wire()}
function wire(){const p=active,click=(id,fn)=>{const e=$(id);if(e)e.onclick=()=>{fn();persist();draw();toast("Saved.")}};
click("saveScript",()=>p.script=$("script").value);
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

// Media Lab: submit and poll durable backend jobs.
const mediaBase=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
async function runMediaJob(kind,input,statusId,buttonId){
  const status=$(statusId),button=$(buttonId);if(!status||!button)return null;
  button.disabled=true;status.textContent="Submitting "+kind+" job…";
  try{
    const response=await fetch(mediaBase+"/api/jobs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({projectId:p.id,kind,input,output:{}})});
    const created=await response.json().catch(()=>({}));
    if(!response.ok)throw new Error(created.detail||"Backend rejected the job ("+response.status+").");
    for(let i=0;i<450;i++){
      await new Promise(resolve=>setTimeout(resolve,2000));
      const check=await fetch(mediaBase+"/api/jobs/"+encodeURIComponent(created.jobId));
      const job=await check.json().catch(()=>({}));
      if(!check.ok)throw new Error(job.detail||"Could not read job status.");
      status.textContent=(job.message||job.status)+" "+(job.progress||0)+"%";
      if(job.status==="failed")throw new Error(job.error||"Generation failed.");
      if(job.status==="completed")return job.output||{};
    }
    throw new Error("Job is still running. Check again after the backend finishes.");
  }catch(error){status.textContent=error.message;return null}
  finally{button.disabled=false}
}
const makeImage=$("makeImage");
if(makeImage)makeImage.onclick=async()=>{
  const prompt=$("mediaImagePrompt").value.trim();if(!prompt){$("imageJobStatus").textContent="Enter an image prompt.";return}
  const out=await runMediaJob("image",{prompt,width:+$("mediaImageWidth").value,height:+$("mediaImageHeight").value},"imageJobStatus","makeImage");
  if(out?.filename){p.media.images.push(out);persist();draw();toast("Image generated.");}
};
const makeVideo=$("makeVideo");
if(makeVideo)makeVideo.onclick=async()=>{
  const selected=[...document.querySelectorAll("[data-media-image]:checked")].map(e=>p.media.images[+e.dataset.mediaImage]?.filename).filter(Boolean);
  if(!selected.length){$("videoJobStatus").textContent="Generate and select at least one image.";return}
  const out=await runMediaJob("video",{images:selected,secondsPerImage:+$("mediaSeconds").value},"videoJobStatus","makeVideo");
  if(out?.filename){p.media.video=out;persist();draw();toast("Video assembled.");}
};
const makeMusic=$("makeMusic");
if(makeMusic)makeMusic.onclick=async()=>{
  const out=await runMediaJob("music",{mood:$("mediaMusicMood").value,duration:+$("mediaMusicDuration").value},"musicJobStatus","makeMusic");
  if(out?.filename){p.media.music=out;persist();draw();toast("Original music generated.");}
};
const makeExport=$("makeExport");
if(makeExport)makeExport.onclick=async()=>{
  if(!p.media.video){$("exportJobStatus").textContent="Create a video first.";return}
  const out=await runMediaJob("render",{video:p.media.video.filename,audio:p.media.music?.filename||null},"exportJobStatus","makeExport");
  if(out?.filename){p.media.export=out;persist();draw();toast("Final MP4 rendered.");}
};
const voiceButton=$("generateVoice");
if(voiceButton)voiceButton.onclick=async()=>{
  const status=$("voiceStatus"),text=$("voiceText").value.trim(),player=$("voicePlayer");
  if(!text){status.textContent="Enter dialogue first.";return}
  const base=(window.MYTUBE_API_BASE||window.location.origin).trim().replace(/\/$/,"");
  const first=Object.values(p.voices||{})[0]||{};
  voiceButton.disabled=true;status.textContent="Generating local speech preview…";player.style.display="none";
  try{
    const response=await fetch(base+"/api/voice/generate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({projectId:p.id,text,style:first.style||"Warm",delivery:first.delivery||"Conversational"})});
    const data=await response.json().catch(()=>({}));
    if(!response.ok)throw new Error(data.detail||"Voice generation failed ("+response.status+").");
    player.src=base+data.audioUrl;player.style.display="block";player.load();
    status.textContent="Preview generated with "+data.engine+".";
  }catch(e){status.textContent=e.message}
  finally{voiceButton.disabled=false}
};
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
async function checkEngine(){if(!engineStatus)return;engineStatus.textContent="Connecting…";try{const r=await fetch(location.origin+"/health",{cache:"no-store"});if(!r.ok)throw Error();const d=await r.json();const a=d.adapters||{},t=a.text;engineStatus.textContent=d.status==="ok"?"Backend online · capability status below.":"Engine responded but is not ready.";const put=(id,value)=>{const el=$(id);if(el)el.textContent=value};put("capText",t?.installed?"Ready · "+t.model:"Backend online; local model unavailable");put("capImage",a.image?.configured?"Endpoint configured; adapter verification pending":"No image engine connected");put("capVideo",a.video?.configured?"Endpoint configured; adapter verification pending":"No video engine connected");put("capVoice",a.voice?.available?"Ready · local eSpeak NG":"Install eSpeak NG for local voice generation");put("capMusic",a.music?.configured?"Endpoint configured; adapter verification pending":"No music engine connected");put("capRender",a.render?.ffmpeg_installed?"FFmpeg installed · MP4 workflow not connected":"FFmpeg not installed")}catch{engineStatus.textContent="Engine offline. Reopen this studio when its Codespace is running."}}
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