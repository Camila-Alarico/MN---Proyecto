import {readFile,writeFile,copyFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../',import.meta.url));
const destination=path.join(root,'static/fonts');
await mkdir(destination,{recursive:true});
let css='/* Local WOFF2 subsets from Fontsource 5.3.0; SIL OFL licenses in static/fonts. */\n';
for(const [pkg,family,weight,suffix,source] of [
 ['@fontsource-variable/ibm-plex-sans','IBM Plex Sans','100 700','wght-normal','wght.css'],
 ['@fontsource/ibm-plex-mono','IBM Plex Mono','400','400-normal','400.css'],
 ['@fontsource-variable/inter','Inter','100 900','wght-normal','wght.css'],
]){
 const directory=path.join(root,'node_modules',pkg);
 const sourceCss=await readFile(path.join(directory,source),'utf8');
 const name=pkg.split('/').at(-1);
 for(const subset of ['latin','latin-ext']){
  const filename=`${name}-${subset}-${suffix}.woff2`;
  const block=sourceCss.split('@font-face').find(part=>part.includes(filename));
  const coverage=block?.match(/unicode-range: ([^;]+);/)?.[1];
  if(!coverage)throw new Error(`Missing font coverage: ${filename}`);
  await copyFile(path.join(directory,'files',filename),path.join(destination,filename));
  css+=`@font-face {\n  font-family: '${family}';\n  font-style: normal;\n  font-weight: ${weight};\n  font-display: swap;\n  src: url('../fonts/${filename}') format('woff2');\n  unicode-range: ${coverage};\n}\n`;
 }
 await copyFile(path.join(directory,'LICENSE'),path.join(destination,`${name}-OFL.txt`));
}
await writeFile(path.join(root,'static/css/fonts.css'),css);
console.log('Local Inter and Plex fonts, coverage and licenses synchronized.');
