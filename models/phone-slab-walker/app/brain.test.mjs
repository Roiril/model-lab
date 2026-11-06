// node --test models/phone-slab-walker/app/brain.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { decide, describeState, parseState, trimFromYaw } from './brain.mjs';
import { chooseLink, findCdc, lineCoding } from './transport.mjs';

test('気分を切ると必ず聞く', () => {
  for (const random of [0, 0.1, 0.99]) assert.equal(decide('W', { moody: false, random }).obey, true);
});

test('断るのは 2 回まで。3 回目は必ず聞く', () => {
  let refused = 0;
  const first = decide('W', { moody: true, refused, random: 0 });
  assert.equal(first.obey, false);
  refused = first.refused;
  const second = decide('W', { moody: true, refused, random: 0.99 });
  assert.equal(second.obey, false);
  refused = second.refused;
  const third = decide('W', { moody: true, refused, random: 0 });
  assert.equal(third.obey, true);
  assert.equal(third.refused, 0);
});

test('機嫌がよければ聞く', () => {
  assert.equal(decide('L', { moody: true, random: 0.5 }).obey, true);
});

test('操舵は向きのずれの逆で、上限で止まる', () => {
  assert.equal(trimFromYaw(3), -3);
  assert.equal(trimFromYaw(-3), 3);
  assert.equal(trimFromYaw(90), -8);
  assert.equal(trimFromYaw(-90), 8);
  assert.equal(trimFromYaw(3, true), 3);
  assert.ok(Object.is(trimFromYaw(0), 0));
  assert.ok(Object.is(trimFromYaw(0.2), 0));
});

test('ファームの返事を読む', () => {
  assert.equal(parseState('hello'), null);
  assert.equal(parseState('{broken'), null);
  assert.deepEqual(parseState('{"ok":true}'), { ok: true });
});

test('片方の脚が無くても表示できる。脚の情報が無い返事は前を残す', () => {
  const line = '{"mode":"idle","left":null,"right":{"id":2,"raw":2050,"deg":0.2,"load":0,"dV":120,"tempC":31,"status":0}}';
  const text = describeState(parseState(line));
  assert.match(text, /左脚: 見つかりません/);
  assert.match(text, /右脚: 0\.2° 31℃ 12\.0V/);
  assert.equal(describeState({ ok: true }, '前の表示'), '前の表示');
});

test('Android は USB、パソコンは Serial を選ぶ', () => {
  const android = 'Mozilla/5.0 (Linux; Android 15; Pixel 7a) Chrome/150';
  assert.equal(chooseLink({ userAgent: android, usb: {}, serial: {} }), 'usb');
  assert.equal(chooseLink({ userAgent: android, serial: {} }), 'serial');
  assert.equal(chooseLink({ userAgent: 'Windows NT', usb: {}, serial: {} }), 'serial');
  assert.equal(chooseLink({ userAgent: 'iPhone' }), null);
});

test('USB の構成から CDC の口を探す。HID は取らない', () => {
  const alt = (interfaceClass, endpoints = []) => ({ interfaceClass, endpoints });
  const cdc = findCdc({ interfaces: [
    { interfaceNumber: 0, alternates: [alt(2, [{ direction: 'in', endpointNumber: 1 }])] },
    { interfaceNumber: 1, alternates: [alt(10, [{ direction: 'out', endpointNumber: 2 }, { direction: 'in', endpointNumber: 3 }])] },
    { interfaceNumber: 2, alternates: [alt(3, [{ direction: 'in', endpointNumber: 4 }])] },
  ] });
  assert.deepEqual(cdc, { control: 0, data: 1, in: 3, out: 2 });
  assert.throws(() => findCdc({ interfaces: [{ interfaceNumber: 2, alternates: [alt(3)] }] }));
});

test('通信速度は 115200。1200 だと Leonardo が書き込み待ちへ入る', () => {
  const bytes = lineCoding();
  assert.equal(new DataView(bytes.buffer).getUint32(0, true), 115200);
  assert.equal(bytes[6], 8);
});
