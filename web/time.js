function timestamp()
{
  now = new Date;
  return now.getTime()
};
exports.timestamp = timestamp


function time()
{
  now = new Date();
  return now;
};
exports.time = time


function log(msg)
{
  now = time();
  console.log('(' + now.getHours() + ":" + now.getMinutes() + ":" +
              now.getSeconds() + '.' + now.getMilliseconds() + ") " + msg);
};
exports.log = log;

