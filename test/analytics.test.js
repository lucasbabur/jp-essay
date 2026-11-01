import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const code = fs.readFileSync(new URL('../landing/analytics.js', import.meta.url), 'utf8');
function track({ua='',referrer='',search='',saved=null}={}) {
  const tags={};
  vm.runInNewContext(code,{URL,URLSearchParams,Date,navigator:{userAgent:ua},location:{hostname:'jpessay.com',pathname:'/',search},sessionStorage:{getItem:()=>JSON.stringify(saved),setItem:()=>{}},window:{clarity:(cmd,k,v)=>{if(cmd==='set')tags[k]=v;}},document:{referrer,createElement:()=>({}),head:{appendChild:()=>{}},addEventListener:()=>{}}});
  return tags;
}
for(const token of ['Twitter for iPhone/12.26','TwitterAndroid/12.28.0-alpha.01']) {
 test(`infer X from explicit app token ${token}`,()=>{
  // Android versions may contain a suffix; real UA continues after a space.
  const tags=track({ua:`Mozilla/5.0 Mobile ${token} Device`});
  assert.equal(tags.traffic_source,'x');assert.equal(tags.attribution_method,'app_user_agent');
 });
}
test('plain browsers and generic Twitter mentions remain unknown',()=>{
 for(const ua of ['Mozilla/5.0 iPhone Safari/604.1','Mozilla/5.0 Android Chrome/151','Twitter','FakeTwitterAndroid/12.0'])assert.equal(track({ua}).traffic_source,'direct_or_unknown');
});
test('explicit and retained attribution take priority over app context',()=>{
 const ua='Mobile Twitter for iPhone/12.26';
 for(const input of [{search:'?utm_source=reddit'},{referrer:'https://reddit.com/'},{saved:{source:'reddit',medium:'social',method:'referrer',capturedAt:Date.now()}}])assert.equal(track({ua,...input}).traffic_source,'reddit');
});
test('old unknown attribution can be improved',()=>{
 assert.equal(track({ua:'Mobile Twitter for iPhone/12.26',saved:{source:'direct_or_unknown',capturedAt:Date.now()}}).traffic_source,'x');
});
test('existing X referrals still work',()=>{
 for(const referrer of ['https://t.co/example','android-app://com.twitter.android/'])assert.equal(track({referrer}).traffic_source,'x');
});
