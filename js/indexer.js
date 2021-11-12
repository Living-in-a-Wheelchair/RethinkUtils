var fs = require("fs");
var path = require("path");
var textract = require('textract');

const MAIN_PATH = "C:\\Users\\arman\\Documents\\ProjectRogerFaulknerRethink\\IPFS_Roger_Dropbox_Archive_Proprietary";

function process(directoryName) {
  fs.readdir(directoryName, function(e, files) {
    if(e) {
      console.log("Error: ", e);
      return;
    }
    files.forEach(function(file) {
      var fullPath = path.join(directoryName, file);
      fs.stat(fullPath, function(e, f) {
        if(e) {
          console.log("Error: ", e);
        }
        if(f.isDirectory()) {
          process(fullPath);
        } else {
          // Only files will be fed in through this loop.
          let text = textract.fromFileWithPath(fullPath, function(e, t) {
            if(!e) {
              console.log(t);
            }
          });
          // console.log(text);
        }
      });
    });
  });
}

process(MAIN_PATH);
