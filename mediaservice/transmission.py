from dataclasses import dataclass, field
import requests
import json

@dataclass
class TransmissionRequest:
    headers: str = ""
    url: str = "http://100.71.2.30:9091/transmission/rpc"



    def make_request(self, payload, retry=False) -> requests.Response:
        # for some reason the default header value in dataclasses as a dict is a problem
        # i could explode into individual fields and reassemble, but this is good enough
        if not self.headers: self.headers = {'Content-Type': 'application/json'}
        response = requests.post(self.url, headers=self.headers, data=payload)

        # handle cases in which we do not have a session-id or a valid session id
        if response.status_code == 409 and retry == False:
            tid = response.headers.get("X-Transmission-Session-Id")
            
            #add the x-transmission-session-id given to us by transmission to the headers
            self.headers["X-Transmission-Session-Id"] = tid

            print("need new session id, got %s" % tid) # debug statements are cool
            # recursive, but only retry once
            self.make_request(payload, retry=True)

            return response

        return response
        
    def torrent_add(self, magnet_uri):
        magnet_payload = self._generate_magnet_payload(magnet_uri)
        self.make_request(magnet_payload)
       
    def stats(self):
        payload = self._generate_stats_payload()
        r = self.make_request(payload)
        return r

    def get_torrents(self):
        payload = self._torrent_list_payload()
        r = self.make_request(payload)
        return r

    def search_torrents(self, name):
        payload = self._torrent_list_payload()
        r = self.make_request(payload)
        if name in r.text:
            return True
        return False

    def remove_complete_torrents(self):
        payload = self._torrent_list_with_status_payload()
        r = self.make_request(payload)
        
        if r.status_code == 200:
            response_data = json.loads(r.text)
            torrents = response_data.get("arguments", {}).get("torrents", [])
            
            complete_torrent_ids = []
            for torrent in torrents:
                if torrent.get("status") == 0:
                    complete_torrent_ids.append(torrent.get("id"))
            
            if complete_torrent_ids:
                remove_payload = self._generate_remove_payload(complete_torrent_ids)
                return self.make_request(remove_payload)
        
        return r

    def _generate_stats_payload(self):
        payload = {
            "method": "session-stats",
            "arguments":{}
        }
        return json.dumps(payload)

    def _generate_magnet_payload(self, magnet_uri):
        payload = {
            "method": "torrent-add",
            "arguments": {
                "filename": magnet_uri
            }
        }
        
        return json.dumps(payload)

    def _torrent_list_payload(self):
        payload = {
            "method": "torrent-get",
            "arguments": {
                "fields": ["id", "name", "magnetLink"]
            }
        }
        return json.dumps(payload)

    def _torrent_list_with_status_payload(self):
        payload = {
            "method": "torrent-get",
            "arguments": {
                "fields": ["id", "name", "status"]
            }
        }
        return json.dumps(payload)

    def _generate_remove_payload(self, torrent_ids):
        payload = {
            "method": "torrent-remove",
            "arguments": {
                "ids": torrent_ids,
                "delete-local-data": False
            }
        }
        return json.dumps(payload)

if __name__ == "__main__":
    t = TransmissionRequest()
    print(t.stats())
