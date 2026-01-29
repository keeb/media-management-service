"""
Image download utilities for SuicideGirls content.
"""

import os
import requests

from mediaservice.db.mongo import get_pending_queue, get_completed_jobs
from mediaservice.sources.suicidegirls import Payload
from mediaservice.util.file import check_folder


def download_image(url: str) -> bytes:
    """Download image from URL.

    Args:
        url: Image URL to download

    Returns:
        Image data as bytes
    """
    print("downloading: %s" % url)
    r = requests.get(url, allow_redirects=True)
    return r.content


def save_image(filename: str, data: bytes) -> None:
    """Save image data to file.

    Args:
        filename: Path to save image to
        data: Image bytes to save
    """
    with open(filename, "wb") as f:
        f.write(data)


def get_work() -> Payload:
    """Get next work item from pending queue.

    Returns:
        Payload object from queue

    Raises:
        SystemExit: If no work available
    """
    print("getting some work")
    record = get_pending_queue().find_one()
    if record is None:
        print("no work to do, exiting")
        raise SystemExit(1)
    return Payload(record)


def make_count(at: int, max_zero: int = 6) -> str:
    """Create zero-padded count string for filenames.

    Since the filesystem will stop sorting correctly if you do not have
    preceding 0 in a number, we will fill with the appropriate amount of 0's.

    Args:
        at: Current number
        max_zero: Total width of resulting string

    Returns:
        Zero-padded string
    """
    chars = str(at)
    amount_of_zeroes = max_zero - len(chars)

    if amount_of_zeroes <= 0:
        return chars
    return "0" * amount_of_zeroes + chars


def complete_work(payload: Payload) -> None:
    """Mark work as complete, moving from pending to completed.

    Args:
        payload: Payload object to complete
    """
    pending = get_pending_queue()
    jobs = get_completed_jobs()

    if not payload.mongo():
        print("something is wrong this is not a mongo object")
        raise SystemExit(1)

    if pending.find_one({"_id": payload.unique_id}) is None:
        print("this payload is not in the pending queue.. wtf?")
        print(payload)

    print("inserting into completed jobs collection")
    jobs.insert_one(payload.dict())
    print("deleting from pending queue")
    pending.delete_one({"_id": payload.unique_id})
    print("done")


def process_work(output_directory: str) -> None:
    """Process a single work item from the queue.

    Args:
        output_directory: Base directory for saving images
    """
    if not check_folder(output_directory):
        raise SystemExit(1)

    work = get_work()
    model_path = os.path.join(output_directory, work.model)
    full_path = os.path.join(output_directory, work.model, work.album)

    if not check_folder(model_path):
        os.mkdir(model_path)
    if check_folder(full_path):
        print("something is wrong, this album already exists?")
        print(work)
        raise SystemExit(1)

    os.mkdir(full_path)

    count = 1
    total_images = len(work.images)

    print("time to save some images")
    print("saving to directory: %s" % full_path)
    print("model name is: %s" % work.model)
    print("album name is: %s" % work.album)

    for image in work.images:
        file_name = make_count(count, len(str(total_images)))
        full_file = os.path.join(full_path, file_name + ".jpg")
        count += 1
        data = download_image(image)
        print("saving as: %s" % full_file)
        save_image(full_file, data)

    print("done saving")
    complete_work(work)
