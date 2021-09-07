#!/usr/bin/python3

import time, os, sys
from aliyunpan.cli.cli import Commander # pip3 install aliyunpan
from threading import Thread

class Pan:
    def __init__(self, token, auto_refresh = False) -> None:
        self.c = Commander(refresh_token=token)
        if auto_refresh:
            Thread(daemon=True, target=self.auto_refresh_token).start()

    def auto_refresh_token(self) -> None:
        print('Start to refresh token automatically.')
        while True:
            try:
                self.c.disk.token_refresh()
                print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) + self.c.disk.refresh_token)
                expires_sec = self.c.disk.refresh_token_expires_sec
                if expires_sec > 60:
                    print('Will refresh token after %d s' % (expires_sec - 60))
                    time.sleep(expires_sec - 60)
            except:
                print('WARN: REFRESH TOKEN FAIL!')
                time.sleep(180)
    
    def upload(self, file_path, upload_path='root') -> None:
        result_list = self.c.upload(file_path, upload_path=upload_path)
        print(str(result_list) + 'is uploaded')
    
    def sync(self, file_dir, upload_path='root') -> None:
        for filename in os.listdir(file_dir):
            if not filename.startswith('synced_'):
                file_path = os.path.join(file_dir, filename)
                self.upload(file_path, upload_path)
                os.rename(file_path, os.path.join(file_dir, 'synced_' + filename))

def main(file_dir, upload_path, token):
    file_dir = os.path.abspath(file_dir)
    pan = Pan(token, True)
    while True:
        try:
            pan.sync(file_dir, upload_path)
            time.sleep(60)
        except:
            print('WARN: SYNC FAIL!')
            time.sleep(180)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) >= 3:
        main(args[0], args[1], args[2])
    else:
        print('使用: aliyunpansyncer <src_dir> <dest_dir> <token>')
        print('例如: aliyunpansyncer sync resource thisyouraliyunpanrefreshtoken')
        print('会将本地目录sync里的文件上传到阿里云盘的resource目录里')
        print('注意：名称以 synced_ 开头的文件将不会上传，上传后，本地文件名也会添加上 synced_ 前缀')
        print('token 可以从阿里云盘安卓端的 /sdcard/Android/data/com.alicloud.databox/files/logs/trace/userId/yunpan/latest.log 里搜索 refresh_token 找到')
