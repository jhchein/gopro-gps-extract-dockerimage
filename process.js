const gpmfExtract = require('gpmf-extract');
const goproTelemetry = require(`gopro-telemetry`);
const fs = require('fs');

function bufferAppender(path, chunkSize) {
  return function (mp4boxFile) {
    var stream = fs.createReadStream(path, { highWaterMark: chunkSize });
    var bytesRead = 0;
    stream.on('end', () => {
      mp4boxFile.flush();
    });
    stream.on('data', chunk => {
      var arrayBuffer = new Uint8Array(chunk).buffer;
      arrayBuffer.fileStart = bytesRead;
      mp4boxFile.appendBuffer(arrayBuffer);
      bytesRead += chunk.length;
    });
    stream.resume();
  };
}

gpmfExtract(bufferAppender('input.mp4', 30 * 1024 * 1024))
  .then(extracted => {
    goproTelemetry(extracted, {}, telemetry => {
      fs.writeFileSync('out.json', JSON.stringify(telemetry));
      console.log('Telemetry saved as JSON');
    });
  })
  .catch(error => console.error(error));