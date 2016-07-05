function ajaxRequest(dim){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            data = JSON.parse(xhttp.responseText);

            // console.log("start loading " + data.result.length.toString() + " points.." )
            

            for (i=0; i< data.result.length; i++){ 
                self.postMessage(data.result[i]);

            }

            // console.log("Finished loading points");
        } 
    }
    // console.log("call DBMS for points")
    xhttp.open("POST", "/_call_points_db", true);
    sendCount = dim.toString() + count.toString();
    xhttp.send(sendCount);
}

var count = 0;
self.addEventListener('message', function(e) {
  var data = e.data;
  switch (data.cmd) {
    case 'start':
      // console.log('POINTS WORKER STARTED WITH COUNT: ' + count.toString());
      ajaxRequest(data.dim);
      count += 5;
      break;
    // case 'stop':
    //   self.postMessage('WORKER STOPPED: ' + data.msg +
    //                    '. (buttons will no longer work)');
    //   self.close(); // Terminates the worker.
    //   break;
    default:
      self.postMessage('Unknown command: ' + data.msg);
  };
}, false);