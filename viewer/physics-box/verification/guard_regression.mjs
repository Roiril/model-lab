import {fileURLToPath} from 'node:url';
process.chdir(fileURLToPath(new URL('.',import.meta.url)));
import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {BoxPhysics,initPhysics,DEFAULTS,NUMERICAL_LIMITS} from '../physics.mjs';
await initPhysics();const cad=JSON.parse(fs.readFileSync('../assets/cad.json')),shapes=JSON.parse(fs.readFileSync('../assets/contact_model.json'));
fs.mkdirSync('guard-regression',{recursive:true});const tests=[];
// Synthetic diagnostic latches test the classification policy, not a physical collision result.
for(const [field,value]of [['penetrationMm',NUMERICAL_LIMITS.maxPenetrationMm+.001],['hingeDriftMm',NUMERICAL_LIMITS.maxHingeDriftMm+.001]]){
 const sim=new BoxPhysics(cad,shapes);sim.peak[field]=value;sim.commandTo('open');for(let i=0;i<8/DEFAULTS.dt;i++)sim.step();
 const result={name:'injected_'+field,method:'Synthetic peak diagnostic latch; normal rigid-body motion otherwise unchanged',injectedValue:value,state:sim.command,lidDeg:sim.lidAngle(),numericalPass:sim.numericalAccuracy().pass};
 assert.equal(result.state,'precision_failed');assert.equal(result.numericalPass,false);assert(Math.abs(result.lidDeg-65)<.5);tests.push({...result,pass:true});sim.dispose();
}
// Force only the active CAD convergence report above its threshold, leaving the representative report passing.
// Run the actual verifier's final pass/exit path in an isolated output directory.
let source=fs.readFileSync('verify.mjs','utf8').replace("'../physics.mjs'","'../../physics.mjs'").replaceAll('test-results','guard-regression/logs').replace('../assets/verification.json','guard-regression/forced_convergence_report.json');
assert(source.includes('const output={'));source=source.replace('const output={','activeConvergence.halfDt.maxHingeDriftMm=.031;const output={');
const fixture='guard-regression/forced_convergence_fixture.mjs';fs.writeFileSync(fixture,source);
const proc=spawnSync(process.execPath,[fixture],{cwd:process.cwd(),encoding:'utf8',maxBuffer:2e6});
assert.equal(proc.status,1,proc.stderr);const report=JSON.parse(fs.readFileSync('guard-regression/forced_convergence_report.json'));
assert.equal(report.pass,false);assert(report.results.every(r=>r.pass));assert(report.convergence.halfDt.maxHingeDriftMm<.03);
tests.push({name:'active_convergence_failure_exit',method:'Synthetic active CAD convergence failure; actual verify.mjs pass and exit path executed',forcedHingeDriftMm:.031,representativeConvergencePass:true,outputPass:report.pass,exitCode:proc.status,pass:true});
const result={physicalTest:false,tests,pass:tests.every(t=>t.pass)};fs.writeFileSync('../assets/guard_regression.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
