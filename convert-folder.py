#!/usr/bin/env python3

import os
import subprocess
import argparse

image_name = 'ekeydar/rename-images-1'
    
def main():
    parser = argparse.ArgumentParser(description='Convert images in a folder')
    parser.add_argument('folder', type=str, help='Folder with images')
    parser.add_argument('--no-build', help='Do not build the image', default=False, action='store_true')
    ns = parser.parse_args()
    
    if not os.path.exists(ns.folder): 
        raise RuntimeError(f'Folder {ns.folder} does not exist')  
    
    if not ns.no_build:
        subprocess.run(['docker', 'build',  '.', '-t', image_name])
    subprocess.run(['docker', 'run', '-v', f'{ns.folder}:/home/images', image_name])    


if __name__ == '__main__':
    main()

