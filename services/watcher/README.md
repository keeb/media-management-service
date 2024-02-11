# watcher

Looks at remote directory and sees if any files are available

## Simple implementation

* If already running -> exit
* Look at remote directory
* If no files exist -> exit
* If files exist, download each individually, then delete.
