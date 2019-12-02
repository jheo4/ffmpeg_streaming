const http = require('http');
const url_parser = require('url');
const fs = require('fs');

const timer = require('./time.js');
const fstreamer = require('./file_stream.js');

const addr = null;
const port = 8080;


var onRequest = (req, res)=>{
  var parsed_url = url_parser.parse(req.url, true);
  var stream = process.env['REPO_HOME'] + '/output' + parsed_url.pathname;
  var stream_status = null; // Stream Status: file, pipe, null
  var no_stream = false;
  var req_timestamp = timer.timestamp();

  console.log(stream);

  if(stream === "") {
    timer.log("404 Strem is not specified");
    res.writeHead(404, {'Content-Type': 'text/html'});
    res.end('(404) the requested stream not specified');
    return;
  }
  else {
    try{ fs.statSync(stream); }
    catch(err){ no_stream = true; }

    if(no_stream === false){ stream_status = 'file'; }

    /* TODO: pipe check...
     *  if(no_stream) {
     *    Check pipe
     *  }
     *  if pipe, stream_status = 'pipe'; no_stream = false;
     *  else, no_stream = true;
     */

    if(no_stream) {
      timer.log("404 Strem Not Found");
      res.writeHead(404, {'Content-Type': 'text/html'});
      res.end('(404) the requested stream not found');
      return;
    }
  }
  timer.log("requested stream: " + stream + " (" + req_timestamp + ")");

  if(stream_status === 'file') {
    fstreamer.stream_file(res, stream, req_timestamp);
  }
  //else if(steram_status === 'pipe') {
    // TODO: file stream from pipe
  //}
}

process.argv.splice(1).forEach(function(val, index, array) {
  console.log('process.argv.splice(1).forEach(function(val, index, array)');
  if (index == 0) {
    timer.log("Runnning " + val +" using "+process.execPath+" version "+process.version+" in "+process.cwd());
  }
});

http.createServer(onRequest).listen(8080);
console.log("Server is running on localhost:8080");

