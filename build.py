#!/usr/bin/env python3

import json
import os
import subprocess
import sys


class MainWork:

    def __init__(self):
        self.lsb_release = None
        self.magpie_release = None
        self.os_release = None
        self.verInfo = None

        with open('version.json', 'r') as file:
            self.verInfo = json.loads(file.read())

        with open('build.sample.sh', 'r') as file:
            self.scriptData = file.read()

        self.__clean()
        self.__copyPackages()
        self.__distroInfoProcess()
        self.__scriptBuilding()
        self.__runCommand()
        self.__clean()

    def __distroInfoProcess(self):
        self.lsb_release = (
                """LSB_VERSION=1.4
        DISTRIB_ID=""" + self.verInfo['distro name'] + """
        DISTRIB_RELEASE=""" + self.verInfo['version'] + """
        DISTRIB_CODENAME=""" + self.verInfo['codename'] + """
        DISTRIB_DESCRIPTION=""" + "\"" + self.verInfo['distro name'] + "\""
        )
        self.magpie_release = self.verInfo['distro name'] + " " + self.verInfo['codename']
        self.os_release = (
                """NAME=""" + self.verInfo['distro name'] + """
        PRETTY_NAME=""" + self.verInfo['pretty name'] + """
        ID=""" + self.verInfo['distro name'] + """
        ID_LIKE=""" + self.verInfo['base'] + """
        VERSION_ID=""" + self.verInfo['version'] + """
        ANSI_COLOR="0;36"
        """
        )

        with open('airootfs/etc/skel/.magpie-settings/' + 'lsb-release', 'w') as file:
            file.write(self.lsb_release)

        with open('airootfs/etc/skel/.magpie-settings/' + 'os-release', 'w') as file:
            file.write(self.os_release)

        with open('airootfs/etc/skel/.magpie-settings/' + 'magpie-release', 'w') as file:
            file.write(self.magpie_release)

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

        with open('build.sh', 'w') as file:
            file.write(self.scriptData)
        subprocess.call('chmod +x build.sh', shell=True)
        subprocess.call('mkdir -v airootfs/root', shell=True)
        # subprocess.call('chmod 777 airootfs/root', shell=True)
        subprocess.call('cp -vf root_customizer.sh airootfs/root/customize_airootfs.sh', shell=True)
        subprocess.call('cp -vf .automated_script.sh airootfs/root/.automated_script.sh', shell=True)
        subprocess.call('chmod +x airootfs/root/customize_airootfs.sh', shell=True)
        subprocess.call('chmod 777 airootfs/root/customize_airootfs.sh', shell=True)

    def __copyPackages(self):
        subprocess.call('cp -avr packages airootfs/etc/skel/', shell=True)

    def __runCommand(self):
        check: int = os.system('./build.sh -v')
        if check is 0:
            os.system('chmod 777 ISO_Image ISO_Image/*')

    def __clean(self):
        clean()


def clean():
    subprocess.call('rm -rf airootfs/root', shell=True)
    subprocess.call('rm -rf build.sh build_work', shell=True)
    subprocess.call('rm -rf airootfs/etc/skel/packages', shell=True)
    subprocess.call('rm -rf airootfs/etc/skel/.magpie-settings/os-release', shell=True)
    subprocess.call('rm -rf airootfs/etc/skel/.magpie-settings/lsb-release', shell=True)
    subprocess.call('rm -rf airootfs/etc/skel/.magpie-settings/magpie-release', shell=True)
    print('Cleaned..')


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
