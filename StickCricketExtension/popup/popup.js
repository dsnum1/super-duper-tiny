
const { SerialPort, ReadlineParser } = require('serialport')

console.log('This is a popup!');

const port = new SerialPort({
    path: 'COM12',
    baudRate: 57600,
  })
  
const parser = new ReadlineParser()
port.pipe(parser);
parser.on('data', console.log);
port.write('ROBOT PLEASE RESPOND\n')
