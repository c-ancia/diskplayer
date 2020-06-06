import pyudev, os
from subprocess import Popen, PIPE, check_output, run
from src.loghandler import Logger, LoggerType

logger = Logger("mount.log")
logger.writeLog("Start.", LoggerType.INFO)

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by("block", "disk")

for device in iter(monitor.poll, None):
    #Capturing only for the desired device and event
    if device == pyudev.Devices.from_device_file(context, '/dev/sda') and device.action == 'change':
        logger.writeLog("Media change detected on device /dev/sda", LoggerType.INFO)
        logger.writeLog("Check media presence...", LoggerType.INFO)
        output = Popen(["lsblk","-o", "NAME"], stdout=PIPE)
        check_presence = Popen(["grep", "sda"], stdin=output.stdout, stdout=PIPE).communicate()[0]
        output.stdout.close()
        #Floppy inserted: we need to mount it and run the script with its path
        if len(check_presence) != 0:
            logger.writeLog("Device exists on machine.", LoggerType.INFO)
            logger.writeLog("Check if media already mounted...", LoggerType.INFO)
            #Avoid throttling
            check_mount = os.path.ismount("/media/floppy")
            if check_mount:
                logger.writeLog("Media already mounted. Event ignored.", LoggerType.INFO)
            else:
                logger.writeLog("Media not mounted", LoggerType.INFO)
                logger.writeLog("Mounting device /dev/sda on /media/floppy.", LoggerType.INFO)
                run(["/usr/bin/systemd-mount", "/dev/sda", "/media/floppy"])
                logger.writeLog("Running diskplayer script.", LoggerType.INFO)
                run(["python3", "/home/carole/projects/diskplayer/main.py", "--path", "/media/floppy/diskplayer.contents"])
        else:
            #Floppy removed: we need to stop the playback and unmount the floppy
            logger.writeLog("Device does not exist on machine.", LoggerType.INFO)
            logger.writeLog("Unmounting device /media/floppy.", LoggerType.INFO)
            run(["/usr/bin/systemd-mount","--umount","/media/floppy"])
            logger.writeLog("Stopping diskplayer script.", LoggerType.INFO)
            run(["python3", "/home/carole/projects/diskplayer/main.py", "--pause"])
        logger.writeLog("End.", LoggerType.INFO)
