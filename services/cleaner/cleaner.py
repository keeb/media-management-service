#!/usr/bin/env python3

import sys
sys.path.append('.')
from transmission import TransmissionRequest
import json

def main():
    t = TransmissionRequest()

    print('Testing updated remove_complete_torrents method...')
    print()

    # First check current torrents
    print('Current torrents:')
    r = t.get_torrents()
    if r.status_code == 200:
        data = json.loads(r.text)
        torrents = data.get('arguments', {}).get('torrents', [])
        print(f'Found {len(torrents)} torrents before removal')
        for torrent in torrents:
            print(f'  ID: {torrent.get("id")}, Name: {torrent.get("name", "unnamed")}')

    print()
    print('Running remove_complete_torrents()...')

    # Test the method
    result = t.remove_complete_torrents()

    if result and result.status_code == 200:
        response_data = json.loads(result.text)
        print(f'Success! Response: {json.dumps(response_data, indent=2)}')
        
        # Check torrents after removal
        print()
        print('Checking torrents after removal...')
        check_result = t.get_torrents()
        if check_result.status_code == 200:
            check_data = json.loads(check_result.text)
            remaining = check_data.get('arguments', {}).get('torrents', [])
            print(f'Remaining torrents: {len(remaining)}')
            for torrent in remaining:
                print(f'  ID: {torrent.get("id")}, Name: {torrent.get("name", "unnamed")}')
        
    elif result:
        print(f'Error: Status {result.status_code}')
        print(f'Response: {result.text}')
    else:
        print('No stopped torrents found to remove')

if __name__ == "__main__":
    main()