
# main functionality

happy path usecase is as follows

* new container is started with a `magnetURI`
* our app then downloads the `magnet` content into `temporary` directory
* once the download is completed, `magnet` content is stored in a `save` directory
* the save directory is available as a volume for easy mounting/copying

edge cases (outside of basic error handling) to consider are
* what happens when the file is not very popular? do we keep it running forever?
* what happens when there's too many of these contain-magnets running at once? is that possible? meaning in this case if there's going to be some contention around running multiple `sessions` on the same host from a network standpoint or anything else like that.
* resuming is going to be supported
* multiple downloads/magnets per container is an anti-pattern for this usecase

# TODO to figure out

*  check to see if there's a partial in `/incomplete` folder
    * if yes, we restart the torrent

* check to see if there's anything in the `/save` folder
    * if so, we error and just exit
    
* what to do with the alerts `session.pop_alerts()` in general
    * one idea is to store in a logfile
    * another idea is to push this somewhere like loki
    * one idea is to just not worry about it at all
    * ?

* what is `ses.post_torrent_updates()` ?

