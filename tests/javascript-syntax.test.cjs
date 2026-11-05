const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync,readdirSync}=require('node:fs');
const {join,resolve}=require('node:path');
const {SourceTextModule}=require('node:vm');

test('all browser modules compile as ECMAScript modules',()=>{
  const root=resolve(__dirname,'../static/js');
  const files=readdirSync(root,{recursive:true}).filter(name=>name.endsWith('.js')).map(name=>join(root,name));
  for(const file of files){
    assert.doesNotThrow(()=>new SourceTextModule(readFileSync(file,'utf8'),{identifier:file}),file);
  }
});
