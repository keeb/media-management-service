#!/usr/bin/env python3
"""
CLI tool to clean completed torrents from Transmission.
"""

import json
from mediaservice.download.transmission import TransmissionRequest


def main():
    t = TransmissionRequest()

    print('Checking current torrents...')
    r = t.get_torrents()
    if r.status_code == 200:
        data = json.loads(r.text)
        torrents = data.get('arguments', {}).get('torrents', [])
        print(f'Found {len(torrents)} torrents')
        for torrent in torrents:
            print(f'  ID: {torrent.get("id")}, Name: {torrent.get("name", "unnamed")}')

    print()
    print('Removing completed torrents...')

    result = t.remove_complete_torrents()

    if result and result.status_code == 200:
        response_data = json.loads(result.text)
        print(f'Success!')

        # Check torrents after removal
        check_result = t.get_torrents()
        if check_result.status_code == 200:
            check_data = json.loads(check_result.text)
            remaining = check_data.get('arguments', {}).get('torrents', [])
            print(f'Remaining torrents: {len(remaining)}')

    elif result:
        print(f'Error: Status {result.status_code}')
        print(f'Response: {result.text}')
    else:
        print('No completed torrents found to remove')


if __name__ == "__main__":
    main()
