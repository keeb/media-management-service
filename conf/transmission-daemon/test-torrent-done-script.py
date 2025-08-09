#!/usr/bin/env python3

import os
import subprocess
import sys

def test_torrent_done_script():
    """
    Test the torrent-done-script.py by simulating transmission environment variables
    """
    
    # Set up test environment variables that transmission would normally provide
    test_env = os.environ.copy()
    test_env['TR_TORRENT_NAME'] = 'South Park S27E02 Got A Nut 1080p AMZN WEB-DL DDP5 1 H 264-FLUX[EZTVx.to].mkv'
    test_env['TR_TORRENT_DIR'] = '/home/keeb/media/video/staging'
    
    script_path = '/storage/02/code/projects/media-management-service/conf/transmission-daemon/torrent-done-script.py'
    
    print(f"Testing torrent-done-script.py with test file:")
    print(f"  TR_TORRENT_NAME: {test_env['TR_TORRENT_NAME']}")
    print(f"  TR_TORRENT_DIR: {test_env['TR_TORRENT_DIR']}")
    print(f"  Script path: {script_path}")
    print()
    
    try:
        # Run the script with test environment
        result = subprocess.run(
            ['python3', script_path],
            env=test_env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("Script output:")
        print(result.stdout)
        
        if result.stderr:
            print("Script errors:")
            print(result.stderr)
        
        print(f"Script exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Script executed successfully!")
        else:
            print("❌ Script failed!")
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out!")
    except Exception as e:
        print(f"❌ Error running script: {e}")

if __name__ == '__main__':
    test_torrent_done_script()