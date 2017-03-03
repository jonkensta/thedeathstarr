#!/usr/bin/python

import os
import getpass
import argparse
import itertools

import ftputil


def ftp_sync_dirs(lroot, ldirs, rroot, rdirs, host_ftp):
    update = set(ldirs).difference(rdirs)
    for dir_ in update:
        dpath = os.path.join(rroot, dir_)
        print("Adding directory {} ...".format(dpath))
        host_ftp.mkdir(dpath)

    remove = set(rdirs).difference(ldirs)
    for dir_ in remove:
        dpath = os.path.join(rroot, dir_)
        print("Removing directory {} ...".format(dpath))
        host_ftp.rmtree(dpath)


def ftp_sync_files(lroot, lfiles, rroot, rfiles, host_ftp):
    update = set(lfiles).difference(rfiles)
    for file_ in update:
        src = os.path.join(lroot, file_)
        dst = os.path.join(rroot, file_)
        print("Adding file {} ...".format(src))
        host_ftp.upload(src, dst)

    remove = set(rfiles).difference(lfiles)
    for file_ in remove:
        fpath = os.path.join(rroot, file_)
        print("Removing file {} ...".format(fpath))
        host_ftp.remove(fpath)

    intersection = set(lfiles).intersection(rfiles)
    for file_ in intersection:
        src = os.path.join(lroot, file_)
        dst = os.path.join(rroot, file_)
        print("Updating file {} ...".format(src))
        host_ftp.upload_if_newer(src, dst)


def ftp_sync_folder(src, dst, host_ftp):
    lhs = os.walk(src)
    rhs = host_ftp.walk(dst)
    zipped = itertools.izip(lhs, rhs)

    for (lroot, ldirs, lfiles), (rroot, rdirs, rfiles) in zipped:
        ldirs.sort()
        ftp_sync_dirs(lroot, ldirs, rroot, rdirs, host_ftp)

        rdirs[:] = map(unicode, ldirs)  # noqa
        ftp_sync_files(lroot, lfiles, rroot, rfiles, host_ftp)


def main():
    parser = argparse.ArgumentParser(description="FTP deploy script")
    parser.add_argument('--hostname')
    parser.add_argument('--username')
    parser.add_argument('--password')

    args = parser.parse_args()

    if args.hostname:
        host = args.hostname
    else:
        host = raw_input("Please enter FTP hostname: ")  # noqa

    if args.username:
        user = args.username
    else:
        user = raw_input("Please enter FTP username: ")  # noqa

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Please enter FTP password: ")

    with ftputil.FTPHost(host, user, password) as ftp_host:
        ftp_sync_folder('deploy', 'thedeathstarr', ftp_host)


if __name__ == '__main__':
    main()
