__author__ = 'https://github.com/password123456/'

import os
import sys
import importlib
import json
import requests
import csv
from datetime import datetime

importlib.reload(sys)

_today_ = datetime.today().strftime('%Y-%m-%d')
_ctime_ = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

_home_path_ = 'F:/code/pythonProject/collect_cloud_ips'
_db_ = '%s/db/%s-cloud_ipinfo.csv' % (_home_path_, _today_)

_headers_ = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) \
             Chrome/49.0.2623.112 Safari/537.36', 'Content-Type': 'application/json; charset=utf-8'}


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    
def collect_oracle_cloud_ips():

    _url = 'https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json'
    _oracle_file = '%s/oracle.json' % _home_path_
    _name_ = 'ORACLE'

    if os.path.exists(_oracle_file):
        create_time = os.stat(_oracle_file).st_ctime
        oracle_file_datetime = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d')
        today = datetime.now().date()

        if str(oracle_file_datetime) == str(today):
            get_oracle_cloud = True
        else:
            get_oracle_cloud = False
    else:
        print('%s[+] Download New %s Cloud File%s' % (Bcolors.OKGREEN, _name_, Bcolors.ENDC))
        r = requests.get(_url, headers=_headers_, verify=True)
        if r.status_code == 200:
            body = r.text
            with open(_oracle_file, 'w') as f:
                f.write(body)
            f.close()
            get_oracle_cloud = True
        else:
            res_status = r.status_code
            message = '**%s_Cloud Collector**\n▶ Connection Error: http %s\n' % (_name_, res_status)
            print(message)
            sys.exit(1)

    if not get_oracle_cloud:
        print('%s[+] Download New %s Cloud File%s' % (Bcolors.OKGREEN, _name_, Bcolors.ENDC))
        r = requests.get(_url, headers=_headers_, verify=True)
        if r.status_code == 200:
            body = r.text
            with open(_oracle_file, 'w') as f:
                f.write(body)
            f.close()
        else:
            res_status = r.status_code
            message = '**%s_Cloud Collector**\n▶ Connection Error: http %s\n' % (_name_, res_status)
            print(message)
            sys.exit(1)
        r.close()

    with open(_oracle_file, 'r') as oracle_file:
        if os.path.exists(_db_):
            mode = 'a'
            header = True
        else:
            mode = 'w'
            header = False

        fa = open(_db_, mode)
        writer = csv.writer(fa, delimiter=',', lineterminator='\n')

        if not header:
            writer.writerow(['datetime', 'platform', 'create_time', 'region', 'ip_prefix', 'service'])

        y = json.load(oracle_file)
        n = 0

        create_time = datetime.strptime(y['last_updated_timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
        create_time = create_time.replace(microsecond=0)
        print('%s[+] Collect Oracle Cloud IP Prefixes.%s' % (Bcolors.OKGREEN, Bcolors.ENDC))

        for item in y['regions']:
            if 'region' in item and 'cidrs' in item:
                region = item['region']
                for item2 in item['cidrs']:
                    n = n + 1
                    ip_prefix = item2['cidr']
                    service = '|'.join(item2['tags'])
                    try:
                        writer.writerow([_ctime_, _name_, create_time, region, ip_prefix, service])
                        sys.stdout.write('\r ----> Processing... %d lines' % n)
                        sys.stdout.flush()
                    except KeyboardInterrupt:
                        sys.exit(0)
                    except Exception as e:
                        print('%s- Exception::%s%s' % (Bcolors.WARNING, e, Bcolors.ENDC))
        fa.close()
    oracle_file.close()
    print('\n')
    
    
def main():
    collect_oracle_cloud_ips()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print('%s- Exception::%s%s' % (Bcolors.WARNING, e, Bcolors.ENDC))
