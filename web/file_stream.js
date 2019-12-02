const fs = require('fs');

var mimes = { // all mime types(https://mzl.la/33ClQyt)
  mp4: 'video/mp4',
  m4s: 'application/octet-stream',
  mpd: 'application/dash+xml'
}


function stream_file(res, stream, timestamp)
{
  var ext = stream.split('.')[1];
  var output_dir = process.env['REPO_HOME'] + '/output'
  if (ext === 'mp4' || ext === 'm4s' || ext === 'mpd') {
    res.statusCode = 200;
    res.setHeader('Content-Type', mimes[ext]);
    res.setHeader('Server-UTC', timestamp);
    var buf = fs.readFileSync(stream);
    res.setHeader('Content-Length', buf.length);
    res.end(buf);
  }
}
exports.stream_file = stream_file;
