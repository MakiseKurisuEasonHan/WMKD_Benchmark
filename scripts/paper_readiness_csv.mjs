import fs from 'node:fs/promises';
import {Workbook} from '@oai/artifact-tool';
const root='C:/Users/Eason/Desktop/WMKD_Benchmark/results/paper_readiness_20260910';
const wb=Workbook.create();
const names=['final_experiment_matrix','final_master_detector_table','final_utility_master','final_model_archive_inventory'];
function col(n){let s='';while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;}
function compact(v){if(v&&typeof v==='object'&&v.source&&'value' in v)return {source:v.source,json_pointer:v.json_pointer,derivation:v.derivation};if(Array.isArray(v))return v.map(compact);if(v&&typeof v==='object')return Object.fromEntries(Object.entries(v).map(([k,x])=>[k,compact(x)]));return v;}
const receipts=[];
for(let i=0;i<names.length;i++){
 const name=names[i];const rows=JSON.parse(await fs.readFile(`${root}/${name}.json`,'utf8'));
 const headers=[...new Set(rows.flatMap(Object.keys))].filter(k=>!['remote_manifest_files'].includes(k));
 const vals=[headers,...rows.map(r=>headers.map(k=>{const v=r[k];return v==null?'NOT_RECORDED':typeof v==='object'?JSON.stringify(compact(v)):v;}))];
 const sh=wb.worksheets.add('Table'+(i+1));const range=sh.getRange(`A1:${col(headers.length)}${vals.length}`);range.values=vals;
 const actual=range.values;if(JSON.stringify(actual)!==JSON.stringify(vals))throw new Error('Cell values changed '+name);
 const q=v=>'"'+String(v).replaceAll('"','""')+'"';await fs.writeFile(`${root}/${name}.csv`,actual.map(r=>r.map(q).join(',')).join('\n')+'\n');
 receipts.push({name,rows:rows.length,columns:headers.length,cell_roundtrip:'PASS'});
}
console.log(JSON.stringify(receipts));
