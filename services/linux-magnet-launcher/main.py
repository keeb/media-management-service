import sys
import requests

test_magnet = "magnet:?xt=urn:btih:2SCTDLAOUOZKOHXMPH7FRFLZTSN7CMHB&dn=%5BSubsPlease%5D%20Mahoutsukai%20ni%20Narenakatta%20Onnanoko%20no%20Hanashi%20-%2003%20%281080p%29%20%5BF29E5418%5D.mkv&xl=1446916156&tr=http%3A%2F%2Fnyaa.tracker.wf%3A7777%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker3.itzmx.com%3A6961%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fretracker.lanta-net.ru%3A2710%2Fannounce&tr=http%3A%2F%2Fopen.acgnxtracker.com%3A80%2Fannounce&tr=wss%3A%2F%2Ftracker.openwebtorrent.com"

def make_request(magnet):
    json_data = {"magnet": magnet}
    response = requests.post("http://hancock:9200/magnet", json=json_data)
    print(response.text)

if __name__ == "__main__":
    magnet = sys.argv[1]
    if not magnet or not magnet.startswith("magnet:"):
        sys.exit("Invalid magnet link")

    make_request(sys.argv[1])
