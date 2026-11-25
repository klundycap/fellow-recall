import re,shutil,os,json,sys
from PIL import Image,ImageDraw
here=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(here,"claude-artifact.html")).read()
out=os.path.dirname(here)  # app lives at the repo root
VERSION=sys.argv[1] if len(sys.argv)>1 else "1"
def rep(s,old,new):
    assert s.count(old)==1,(old[:60],s.count(old));return s.replace(old,new)
s=src
s=rep(s,'<meta name="claude:viewport-fit-sides" content="cover">\n','')
head='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#EEF1F5" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0D1118" media="(prefers-color-scheme: dark)">
<meta name="description" content="Pain medicine flashcards with recall and clinic faces.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
'''
s=head+s
s=rep(s,'</style>\n','html{-webkit-text-size-adjust:100%}body{margin:0}:root{padding-top:env(safe-area-inset-top,0px)}img{max-width:100%}\n</style>\n</head>\n<body>\n')
# settings: API key
s=rep(s,'''    <div class="section">
      <h2>Study and Claude</h2>''','''    <div class="section">
      <h2>Claude API key</h2>
      <p class="note">Ask, Distill and the clinic-face writer use your key from console.anthropic.com. It is saved only on this device and sent only to Anthropic.</p>
      <input type="password" id="apiKey" placeholder="sk-ant-…" autocomplete="off" aria-label="Claude API key">
      <div class="row"><button class="primary" type="button" id="keySave">Save key</button><button class="ghost" type="button" id="keyTest">Test key</button></div>
      <p class="status" id="keyStatus"></p>
    </div>

    <div class="section">
      <h2>Study and Claude</h2>''')
s=rep(s,'''const errMsg=''','''ERR.no_key="Add your Claude API key in Deck › Claude API key first.";ERR.bad_key="Your API key was rejected. Check it in Deck › Claude API key.";ERR.offline="No internet connection. Studying works offline, but drafting cards needs a connection.";ERR.invalid_request="Claude couldn't accept that request. Try a shorter text or check your account's credit.";
const errMsg=''')
s=rep(s,'''setSync("ok","Synced");
    }else{''','''setSync("ok",window.FR_STANDALONE?"Saved":"Synced");
    }else{''')
s=s.replace('setSync("ok","Synced")','setSync("ok",window.FR_STANDALONE?"Saved":"Synced")')
s=s.replace('setSync("busy","Syncing")','setSync("busy",window.FR_STANDALONE?"Loading":"Syncing")')
s=rep(s,'''window.addEventListener("pagehide",''','''if(window.FR_KEY){
  const st=$("#keyStatus");const k=window.FR_KEY.get();$("#apiKey").value=k;st.textContent=k?"A key is saved on this device.":"No key saved yet.";
  $("#keySave").onclick=()=>{const v=$("#apiKey").value.trim();window.FR_KEY.set(v);st.className="status";st.textContent=v?"Key saved on this device.":"Key removed.";};
  $("#keyTest").onclick=async e=>{const v=$("#apiKey").value.trim();if(v)window.FR_KEY.set(v);e.target.disabled=true;st.className="status";st.innerHTML='<span class="spinner"></span>Testing';
    try{await window.FR_KEY.test();st.textContent="The key works."}catch(err){st.className="status err";st.textContent=errMsg(err)}finally{e.target.disabled=false}};
}
document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="hidden"&&(dirty.size||metaDirty))flush()});
window.addEventListener("pagehide",''')
s=rep(s,'<script>\n"use strict";','<script src="anthropic-sdk.js?v='+VERSION+'"></script>\n<script src="shim.js?v='+VERSION+'"></script>\n<script>\n"use strict";')
s+='\n</body>\n</html>\n'
open(os.path.join(out,"index.html"),"w").write(s)
# shim.js and anthropic-sdk.js live at the repo root and are edited there
json.dump({"name":"Fellow Recall","short_name":"Recall","description":"Pain medicine flashcards with recall and clinic faces.",
 "start_url":"./","scope":"./","display":"standalone","orientation":"portrait","background_color":"#EEF1F5","theme_color":"#3D47D9",
 "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png"},
          {"src":"icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},open(os.path.join(out,"manifest.webmanifest"),"w"),indent=1)
open(os.path.join(out,"sw.js"),"w").write('''const CACHE="fellow-recall-v%s";
const SHELL=["./","index.html","shim.js?v=%s","anthropic-sdk.js?v=%s","manifest.webmanifest","icon-192.png","icon-512.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=="GET")return;
  if(u.origin===location.origin){
    // network first for the page so updates arrive; cache for offline
    if(e.request.mode==="navigate"){e.respondWith(fetch(e.request).then(r=>{const c=r.clone();caches.open(CACHE).then(x=>x.put("index.html",c));return r}).catch(()=>caches.match("index.html")));return}
    e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(n=>{const c=n.clone();caches.open(CACHE).then(x=>x.put(e.request,c));return n})));
  }else if(u.hostname==="fonts.googleapis.com"||u.hostname==="fonts.gstatic.com"){
    e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(n=>{const c=n.clone();caches.open(CACHE).then(x=>x.put(e.request,c));return n})));
  }
});
'''%(VERSION,VERSION,VERSION))
# icons: two offset cards, blue recall + amber clinic
def icon(size,maskable=False):
    S=size*4;im=Image.new("RGBA",(S,S),(61,71,217,255) if maskable else (0,0,0,0));d=ImageDraw.Draw(im)
    if not maskable:d.rounded_rectangle([0,0,S-1,S-1],radius=int(S*.22),fill=(61,71,217,255))
    k=0.78 if maskable else 1.0
    def box(x0,y0,x1,y1):c=S/2;return [c+(x0*S-c)*k,c+(y0*S-c)*k,c+(x1*S-c)*k,c+(y1*S-c)*k]
    d.rounded_rectangle(box(.30,.20,.80,.70),radius=int(S*.06*k),fill=(240,163,90,255))
    d.rounded_rectangle(box(.20,.30,.70,.80),radius=int(S*.06*k),fill=(255,255,255,255))
    d.rounded_rectangle(box(.27,.43,.60,.48),radius=int(S*.02*k),fill=(61,71,217,255))
    d.rounded_rectangle(box(.27,.55,.53,.60),radius=int(S*.02*k),fill=(180,186,240,255))
    return im.resize((size,size),Image.LANCZOS)
icon(192).save(os.path.join(out,"icon-192.png"));icon(512).save(os.path.join(out,"icon-512.png"))
icon(180,True).convert("RGB").save(os.path.join(out,"icon-180.png"));icon(512,True).save(os.path.join(out,"icon-maskable-512.png"))
print("built",os.listdir(out))
