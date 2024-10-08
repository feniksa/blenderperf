import argparse
import os

import requests

def get_scene_report(scene_dir):
    pass

def get_assets_list(outdir):
    file_name = os.path.join(outdir, 'assets.txt')

    assets = []
    with open(file_name, "r") as file:
        file_content = file.readline().strip()
        assets.append(file_content)

    return assets

def main():
    parser = argparse.ArgumentParser(
        prog='submit.py',
        description='e test for application',
        epilog='for more information: https://github.com/feniksa/blenderperf')

    default_url = 'https://200volts.com'
    default_outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outdir')

    parser.add_argument('-u', '--url', default=default_url, type=str, help='url for upload')
    parser.add_argument('-a', '--apikey', default='qqq', type=str, help='api token')
    parser.add_argument('-o', '--outdir', default=default_outdir, type=str, help='default outdir with metrics')

    args = parser.parse_args()

    get_assets_list(args.outdir)
    exit(0)

    data = {
        "apikey": "qqqqqqqqq",
        "key2": "value2"
    }

    # Send the POST request and capture the response
    response = requests.post(args.url, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)

if __name__ == "__main__":
    main()