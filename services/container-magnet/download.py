import libtorrent as lt
import sys

from time import sleep

import logging
logging.basicConfig(
    level=logging.DEBUG, 
    filename="torrent.log",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)

settings = {
    'user_agent': 'container_magnet/' + lt.__version__,
    'listen_interfaces': '0.0.0.0:6881',
    'download_rate_limit': 0,
    'upload_rate_limit': 5000,
    'alert_mask': lt.alert.category_t.all_categories,
    'outgoing_interfaces': '',
    'dht_bootstrap_nodes': 'router.bittorrent.com:6881,dht.transmissionbt.com:6881,router.utorrent.com:6881',
    'enable_dht': True,
}


def new_torrent(magnet):
    torrent_object = lt.add_torrent_params()
    torrent_object = lt.parse_magnet_uri(magnet)
    torrent_object.save_path = "/data/incomplete"
    torrent_object.storage_mode = lt.storage_mode_t.storage_mode_sparse
   
    torrent_object.flags |= lt.torrent_flags.duplicate_is_error \
        | lt.torrent_flags.auto_managed \
        | lt.torrent_flags.duplicate_is_error

    return torrent_object

def start_torrent(torrent, session):
    session.async_add_torrent(torrent)

print(settings)

test_magnet = "magnet:?xt=urn:btih:375ae3280cd80a8e9d7212e11dfaf7c45069dd35&dn=archlinux-2023.02.01-x86_64.iso"
ses = lt.session(settings) # main session for the torrent client
torrent = new_torrent(test_magnet)
start_torrent(torrent, ses)
torrents = []

while True:
    alerts = ses.pop_alerts()

    for a in alerts:
        # handle the following alerts..

        if isinstance(a, lt.add_torrent_alert): 
            logger.warning("Torrent added")
            logger.debug(a.message())
            h = a.handle
            h.set_max_connections(20)
            h.set_max_uploads(5)
            torrents.append(h)
        if isinstance(a, lt.save_resume_data_failed_alert):
            logger.error("Failed to save resume data")
            logger.debug(a.message())
            sys.exit(1)
        if isinstance(a, lt.save_resume_data_alert): 
            logger.info("resumed a torrent")
            logger.debug(a.message())
        if isinstance(a, lt.state_update_alert):
            for i in a.status:
                h = i.handle
                if h in torrents:
                    logger.info("torrent state update")
                    logger.debug(a.message())

                
        if isinstance(a, lt.torrent_alert):
            logger.info("torrent alert")
            logger.debug(a.message())

        if isinstance(a, lt.torrent_finished_alert):
            logger.info("torrent finished")
            # need to add logic for moving the file
            # consider adding logic to seed to a particular threshold before exiting
            exit(0)
        

    # figure out how to keep a log of the messages and probably store in the in a file somewhere. 
    #logger.info(a.message())
    ses.post_torrent_updates()
    ses.post_dht_stats()

    for t in torrents:
        if t.status().is_finished:
            logger.info("torrent finished")
            # need to add logic for moving the file
            # consider adding logic to seed to a particular threshold before exiting
            exit(0)
        else:
            logger.debug("torrent status: " + str(t.status().state))
            logger.debug("torrent progress: " + str(t.status().progress))
            logger.debug("torrent download rate: " + str(t.status().download_rate))
            logger.debug("torrent upload rate: " + str(t.status().upload_rate))
            logger.debug("torrent total download: " + str(t.status().total_download))




    sleep(1) # otherwise the loop will eat up all the CPU
