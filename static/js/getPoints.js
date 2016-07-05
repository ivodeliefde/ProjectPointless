function ajaxRequest(dim){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            data = JSON.parse(xhttp.responseText);

            // console.log("start loading " + data.result.length.toString() + " points.." )
            
            var count = 0
            for (i=0; i< data.result.length; i++){ 
              if (count == 50) {
                self.postMessage(data.result[i]);
                count = 0;
              } else {
                count++
              }

            }

            // console.log("Finished loading points");
        } 
    }
    // console.log("call DBMS for points")
    xhttp.open("GET", "/_get_points", true);
    xhttp.send();
}

self.addEventListener('message', function(e) {
  var data = e.data;
  switch (data.cmd) {
    case 'start':
      // console.log('POINTS WORKER STARTED WITH COUNT: ' + count.toString());
      ajaxRequest();
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