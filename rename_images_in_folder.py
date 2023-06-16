#!/usr/bin/env python3

#from PIL import Image
import datetime
import functools
import glob
import hashlib
import json
import os
import os.path
import subprocess

PHOTO_EXTS = ['png', 'jpg', 'jpeg', 'heic']


@functools.lru_cache(3)
def get_exif(path):
    assert os.path.exists(path)
    exif_data = subprocess.check_output(
        ['exiftool', '-Model', '-DateTimeOriginal', '-j', path], universal_newlines=True)
    return json.loads(exif_data)[0]


def get_date_taken(path):
    # try:
    #     return Image.open(path)._getexif()[36867]
    # except Exception:
    #     return None
    try:
        return get_exif(path)['DateTimeOriginal']
    except Exception:
        return None


def get_model(path):
    """ returns the manufactor """
    # try:
    #     return Image.open(path)._getexif()[272] # 271 for model only
    # except Exception:
    #     return None
    return get_exif(path).get('Model', 'unknown_model')


def is_photo(f):
    fl = f.lower()
    for ext in PHOTO_EXTS:
        if fl.endswith('.' + ext):
            return True
    return False


def get_ext(f):
    return os.path.splitext(f)[1].lower().lstrip('.')


def format_date(f, dt_str, offset):
    # offset in minuets
    try:
        dt = datetime.datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
        if offset:
            dt = dt + datetime.timedelta(minutes=offset)
        return dt.strftime('%Y_%m_%d_%H_%M_%S')
    except ValueError:
        print('Failed to extract datetime for file %s' % f)
        return dt_str.replace(':', '_').replace(' ', '_')


def rename_current_folder(ns):
    files = glob.glob(ns.pat)
    photo_files = [f for f in files if is_photo(f)]
    total_count = len(photo_files)
    for idx, f in enumerate(photo_files, start=1):
        try:
            handle_file(f, ns)
            if idx % 10 == 0:
                print(f'So far {idx}/{total_count}')
        except Exception as e:
            print('Failed to handle file %s: %s' % (f, e))


def get_checksum(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def handle_file(f, ns):
    dt = get_date_taken(f)
    ext = get_ext(f)
    checksum = get_checksum(f)
    if dt:
        model = get_model(f) or 'na'
        model = model.replace(' ', '_').strip('\0')
        offset = 0
        if ns.offset or ns.offset_minutes:
            if ns.offset:
                offset = ns.offset*60
            elif ns.offset_minutes:
                offset = ns.offset_minutes
        prefix = '%s_%s' % (format_date(f, dt, offset=offset), model)
        to_name = '%s_%s.%s' % (prefix, checksum[0:6], ext)
        # suffix = 2
        # if to_name == f:
        #     return
        # while True:
        #     if os.path.exists(to_name):
        #         to_name = '%s_%s.%s' % (prefix,suffix,ext)
        #         suffix+=1
        #     else:
        #         break
        # assert not os.path.exists(to_name)
    else:
        print('Could not get exif data for %s' % f)
        if ns.use_mtime:
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(f))
            prefix = mt.strftime('%Y_%m_%d_%H_%M_%S') + '_mt'
        elif ns.use_date:
            prefix = f'{ns.use_date}_man'
        else:
            prefix = 'no_dt'
        to_name = '%s_%s.%s' % (prefix, checksum[0:6], ext)
    if f != to_name:
        if ns.verbose:
            print(f'Rename {f} to {to_name}')
        os.rename(f, to_name)
    else:
        if ns.verbose:
            print(f'same file {f} - no op')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--offset', type=float)
    parser.add_argument('--offset-minutes', type=float)
    parser.add_argument('--offset-pattern')
    parser.add_argument('--cd')
    parser.add_argument('--pat', default='*')
    parser.add_argument('--use-mtime', action='store_true')
    parser.add_argument('--use-date', type=str)
    parser.add_argument('--verbose', action='store_true', default=False)
    ns = parser.parse_args()
    print(ns)
    if ns.cd:
        os.chdir(ns.cd)
    rename_current_folder(ns)


if __name__ == '__main__':
    main()
