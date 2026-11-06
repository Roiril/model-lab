// スマホ・パソコンと Leonardo をつなぐ口。
//
// Android の Web Serial は Android 17 以降で、配線のシリアルポートを見せる端末だけが対象
// （Chrome 148 の Intent to Ship）。Pixel で使えるとは限らないので、Android では WebUSB で
// USB-CDC を直接話す。Windows の WebUSB は OS のドライバが CDC を掴むので、パソコンは Web Serial。

const USB_FILTERS = Object.freeze([
  { vendorId: 0x2341 },   // Arduino
  { vendorId: 0x2a03 },   // arduino.org
  { vendorId: 0x1b4f },   // SparkFun（互換品）
  { classCode: 2 },       // CDC の口を持つ機器
]);
const CDC_CONTROL = 2, CDC_DATA = 10;
const SET_LINE_CODING = 0x20, SET_CONTROL_LINE_STATE = 0x22;
const DTR_AND_RTS = 0x03;
const READ_BYTES = 64;

/** どちらの口を使うか。nav は navigator 相当。 */
export function chooseLink({ userAgent = '', usb, serial } = {}) {
  const android = /Android/i.test(userAgent);
  if (android && usb) return 'usb';
  if (serial) return 'serial';
  if (usb) return 'usb';
  return null;
}

/** USB の構成から CDC の 2 つの口と、データの出入口を探す。無ければ例外。 */
export function findCdc(configuration) {
  const alternateOf = iface => iface.alternates?.[0] ?? iface.alternate;
  const interfaces = configuration.interfaces;
  const control = interfaces.find(iface => alternateOf(iface).interfaceClass === CDC_CONTROL);
  const data = interfaces.find(iface => {
    const alternate = alternateOf(iface);
    return alternate.interfaceClass === CDC_DATA
      && alternate.endpoints.some(e => e.direction === 'in')
      && alternate.endpoints.some(e => e.direction === 'out');
  });
  if (!control || !data) throw new Error('USB シリアルの口が見つかりません');
  const endpoints = alternateOf(data).endpoints;
  return {
    control: control.interfaceNumber,
    data: data.interfaceNumber,
    in: endpoints.find(e => e.direction === 'in').endpointNumber,
    out: endpoints.find(e => e.direction === 'out').endpointNumber,
  };
}

/** 115200 8N1。1200 にすると Leonardo は書き込み待ちへ再起動するので、必ず送る。 */
export function lineCoding() {
  const bytes = new Uint8Array(7);
  new DataView(bytes.buffer).setUint32(0, 115200, true);
  bytes[6] = 8;
  return bytes;
}

export async function openUsbLink(usb) {
  const device = await usb.requestDevice({ filters: [...USB_FILTERS] });
  await device.open();
  if (!device.configuration) await device.selectConfiguration(1);
  const cdc = findCdc(device.configuration);
  await device.claimInterface(cdc.control);
  await device.claimInterface(cdc.data);
  const setup = request => ({ requestType: 'class', recipient: 'interface', request, value: 0, index: cdc.control });
  await device.controlTransferOut(setup(SET_LINE_CODING), lineCoding());
  // DTR を立てないと Leonardo の Serial は送信を捨てる
  await device.controlTransferOut({ ...setup(SET_CONTROL_LINE_STATE), value: DTR_AND_RTS });
  return {
    kind: 'usb',
    write: bytes => device.transferOut(cdc.out, bytes),
    async read() {
      const result = await device.transferIn(cdc.in, READ_BYTES);
      if (result.status !== 'ok') throw new Error(`USB の受信に失敗しました（${result.status}）`);
      return new Uint8Array(result.data.buffer, result.data.byteOffset, result.data.byteLength);
    },
    close: () => device.close(),
  };
}

export async function openSerialLink(serial) {
  const port = await serial.requestPort();
  await port.open({ baudRate: 115200 });
  const writer = port.writable.getWriter();
  const reader = port.readable.getReader();
  return {
    kind: 'serial',
    write: bytes => writer.write(bytes),
    async read() {
      const { value, done } = await reader.read();
      if (done) throw new Error('線が切れました');
      return value;
    },
    async close() {
      reader.releaseLock();
      writer.releaseLock();
      await port.close();
    },
  };
}
