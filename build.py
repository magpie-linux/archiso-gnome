#!/usr/bin/env python3

import json
import os
import subprocess
import sys


class MainWork:

    def __init__(self):
        self.verInfo = None
        self.scriptData = None
        with open('version.json', 'r', encoding='utf-8') as file:
            self.verInfo = json.loads(file.read())
        with open('build.sample.sh', 'r', encoding='utf-8') as file:
            self.scriptData = file.read()
        self.__clean()
        self.__copyProcess()
        self.__distroInfoProcess()
        self.__scriptBuilding()
        self.__runCommand()
        self.__clean()

    # noinspection PyMethodMayBeStatic
    def __distroInfoProcess(self):
        releaseFiles: str = 'airootfs/etc/skel/settings/*-release'
        subprocess.call("sed -i 's|__RELEASE__|{0}|' {1}"
                        .format(self.verInfo['version'], releaseFiles), shell=True)
        subprocess.call("sed -i 's|__CODENAME__|{0}|' {1}"
                        .format(self.verInfo['codename'], releaseFiles), shell=True)

    def __scriptBuilding(self):
        self.scriptData = self.scriptData.replace("#SHELL_LOCATION", "#!/bin/bash")
        self.scriptData = self.scriptData.replace(
            'distro_name="@"', 'distro_name=' + "\"" + self.verInfo['distro name'] + "\"")
        self.scriptData = self.scriptData.replace(
            'iso_name="@"', 'iso_name=' + "\"" + self.verInfo['iso name'] + "\"")
        self.scriptData = self.scriptData.replace(
            'iso_label="@"', 'iso_label=' + "\"" + self.verInfo['iso label'] + "\"")
        self.scriptData = self.scriptData.replace(
            'iso_publisher="@"', 'iso_publisher=' + "\"" + self.verInfo['iso publisher'] + "\"")
        self.scriptData = self.scriptData.replace(
            'iso_application="@"', 'iso_application=' + "\"" + self.verInfo['iso application'] + "\"")

        with open('build.sh', 'w', encoding='utf-8') as file:
            file.write(self.scriptData)
        subprocess.call('chmod +x build.sh', shell=True)

    # noinspection PyMethodMayBeStatic
    def __copyProcess(self):
        subprocess.call('mkdir -v airootfs/root', shell=True)
        # subprocess.call('chmod 777 airootfs/root', shell=True)
        subprocess.call('cp -vf archroot_customizer.sh airootfs/root/customize_airootfs.sh', shell=True)
        subprocess.call('cp -vf automated_script.sh airootfs/root/.automated_script.sh', shell=True)
        subprocess.call('chmod +x airootfs/root/customize_airootfs.sh', shell=True)
        subprocess.call('chmod 777 airootfs/root/customize_airootfs.sh', shell=True)
        subprocess.call('cp -avr packages airootfs/etc/skel/', shell=True)
        subprocess.call('cp -avr settings airootfs/etc/skel/', shell=True)

    # noinspection PyMethodMayBeStatic
    def __runCommand(self):
        check: int = os.system('./build.sh -v')
        if check is 0:
            os.system('chmod 777 ISO_Image ISO_Image/*')

    # noinspection PyMethodMayBeStatic
    def __clean(self):
        clean()


def clean():
    print('Cleaning..')
    subprocess.call('rm -rf airootfs/root', shell=True)
    subprocess.call('rm -rf airootfs/etc/skel/settings', shell=True)
    subprocess.call('rm -rf airootfs/etc/skel/packages', shell=True)
    subprocess.call('rm -rf build.sh', shell=True)
    subprocess.call('rm -rf build_work', shell=True)
    print('Cleaned')


def main():
    arg: list = sys.argv
    if os.getuid() is 0:
        try:
            if len(arg) != 0 and arg[1] == 'clean':
                clean()
                return
        except IndexError:
            pass
        try:
            MainWork()
        except KeyboardInterrupt:
            clean()
            print('error: operation has been canceled by ' + subprocess.getoutput("echo $(whoami)"))
    else:
        print('error: you cannot perform this operation unless you are root.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
# End
