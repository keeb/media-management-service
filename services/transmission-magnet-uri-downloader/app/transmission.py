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
        
    def torrent_add(self, magnet_uri, retry=False):
        magnet_payload = self._generate_magnet_payload(magnet_uri)
        r = self.make_request(magnet_payload)
       

    def _generate_magnet_payload(self, magnet_uri):
        payload = {
            "method": "torrent-add",
            "arguments": {
                "filename": magnet_uri
            }
        }
        
        return json.dumps(payload)

if __name__ == "__main__":
    t = TransmissionRequest()
    t.torrent_add("magnet:?xt=urn:btih:YM33O27TUWET4CNWJZA3GAC46I22OPK5&dn=%5BSubsPlease%5D%20Tokyo%20Mew%20Mew%20New%20-%2024%20%281080p%29%20%5B14CDBD18%5D.mkv&xl=509233156&tr=http%3A%2F%2Fnyaa.tracker.wf%3A7777%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker3.itzmx.com%3A6961%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fretracker.lanta-net.ru%3A2710%2Fannounce&tr=http%3A%2F%2Fopen.acgnxtracker.com%3A80%2Fannounce&tr=wss%3A%2F%2Ftracker.openwebtorrent.com")
