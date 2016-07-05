function ajaxRequest(dim){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            data = JSON.parse(xhttp.responseText);

            // console.log("start loading " + data.result.length.toString() + " boxes.." )
            
            for (i=0; i< data.result.length; i++){ 
                self.postMessage(data.result[i]);

            }

            // console.log("Finished loading empty leaf nodes");
        } 
    }
    // console.log("call DBMS for empty leaf nodes")
    xhttp.open("POST", "/_get_path", true);
    // sendCoords = "77 7224317";
    // sendCoords = "000 1055";
    sendCoords = "003 0157505";
    xhttp.send(sendCoords);
}

self.addEventListener('message', function(e) {
  var data = e.data;
  switch (data.cmd) {
    case 'start':
      // console.log('EMPTY WORKER STARTED WITH COUNT: ' + count.toString());
      ajaxRequest(data.dim);
      // console.log(data.dim);
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