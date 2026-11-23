/* Standalone runtime: stands in for the claude.ai page capabilities.
   db      -> IndexedDB on this device
   user    -> a fixed local id
   sample  -> Claude API with the key saved in Settings (stays on this device)
   downloads -> normal browser download */
(function(){
"use strict";
window.FR_STANDALONE=true;
const KEY_LS="fr-api-key";
const MODEL="claude-opus-5-5";
function idb(){return new Promise((res,rej)=>{const r=indexedDB.open("fellow-recall",1);r.onupgradeneeded=()=>r.result.createObjectStore("docs");r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)})}
const dbp=idb();
function tx(mode,fn){return dbp.then(d=>new Promise((res,rej)=>{const t=d.transaction("docs",mode);const s=t.objectStore("docs");const out=fn(s);t.oncomplete=()=>res(out&&out.result);t.onerror=()=>rej({code:"unavailable",message:String(t.error)});t.onabort=()=>rej({code:"quota_exceeded",message:String(t.error)})}))}
const db={doc(path){return{
  path,
  get:()=>tx("readonly",s=>s.get(path)).then(v=>({id:path.split("/").pop(),exists:v!==undefined,data:()=>v,metadata:{fromCache:false,hasPendingWrites:false}})),
  set:(data)=>tx("readwrite",s=>s.put(JSON.parse(JSON.stringify(data)),path)).then(()=>undefined),
  delete:()=>tx("readwrite",s=>s.delete(path)).then(()=>undefined)
}}};
try{navigator.storage&&navigator.storage.persist&&navigator.storage.persist()}catch(e){}
const user={id:async()=>"local",isOwner:async()=>true,canEdit:async()=>true,can:async()=>true};
let client=null,clientKey=null;
function getClient(){
  let key="";try{key=localStorage.getItem(KEY_LS)||""}catch(e){}
  if(!key)throw {code:"no_key",message:"No API key"};
  if(!client||clientKey!==key){client=new window.Anthropic({apiKey:key,dangerouslyAllowBrowser:true,maxRetries:2});clientKey=key}
  return client;
}
function mapErr(e){
  if(e&&e.code&&!(e instanceof Error))return e;
  const A=window.Anthropic;
  if(e instanceof A.AuthenticationError||e instanceof A.PermissionDeniedError)return {code:"bad_key",message:e.message};
  if(e instanceof A.RateLimitError)return {code:"rate_limited",message:e.message};
  if(e instanceof A.BadRequestError)return {code:"invalid_request",message:e.message};
  if(e instanceof A.APIConnectionError)return {code:"offline",message:e.message};
  if(e instanceof A.APIError)return {code:"upstream_error",message:e.message};
  return {code:"upstream_error",message:String(e&&e.message||e)};
}
function parseJson(text){
  let t=text.trim().replace(/^```(?:json)?\s*/i,"").replace(/```\s*$/,"");
  try{return JSON.parse(t)}catch(e){}
  const a=t.indexOf("{"),b=t.lastIndexOf("}");
  if(a>=0&&b>a){try{return JSON.parse(t.slice(a,b+1))}catch(e){}}
  throw {code:"invalid_json",message:"Reply was not JSON",text};
}
async function ask(prompt,opts){
  opts=opts||{};
  let msg;
  try{
    msg=await getClient().beta.messages.create({
      model:MODEL,max_tokens:16000,
      output_config:{effort:opts.modelTier==="quick"?"low":"medium"},
      betas:["server-side-fallback-2026-07-01"],fallbacks:"default",
      messages:[{role:"user",content:typeof prompt==="string"?prompt:prompt}]
    });
  }catch(e){throw mapErr(e)}
  if(msg.stop_reason==="refusal")throw {code:"refused",message:"Declined"};
  const text=(msg.content||[]).filter(b=>b.type==="text").map(b=>b.text).join("");
  if(!text)throw {code:"empty_completion",message:"No text"};
  return {text,truncated:msg.stop_reason==="max_tokens"};
}
const sample=async(p,o)=>ask(p,o);
sample.json=async(p,o)=>{const r=await ask(p,o);if(r.truncated)throw {code:"invalid_json",message:"Cut short",text:r.text};return parseJson(r.text)};
const downloads={save:async({filename,data})=>{const blob=data instanceof Blob?data:new Blob([data],{type:"application/json"});const u=URL.createObjectURL(blob);const a=document.createElement("a");a.href=u;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),4000);return {status:"saved"}}};
const caps={db,user,sample,downloads};
window.claude={use:n=>Promise.resolve(caps[n]||null)};
window.FR_KEY={get(){try{return localStorage.getItem(KEY_LS)||""}catch(e){return""}},set(v){try{v?localStorage.setItem(KEY_LS,v):localStorage.removeItem(KEY_LS)}catch(e){}},
  async test(){await ask("Reply with the single word OK.",{modelTier:"quick"})}};
if("serviceWorker" in navigator&&(location.protocol==="https:"||location.hostname==="localhost")){navigator.serviceWorker.register("sw.js").catch(()=>{})}
})();
