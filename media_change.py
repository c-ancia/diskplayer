import pyudev, os
from subprocess import Popen, PIPE, run
from src.loghandler import Logger, LoggerType

logger = Logger("mount.log")
logger.write_log("Start.", LoggerType.INFO)

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by("block", "disk")

for device in iter(monitor.poll, None):
    #Capturing only for the desired device and event
    if device == pyudev.Devices.from_device_file(context, '/dev/sda') and device.action == 'change':
        logger.write_log("Media change detected on device /dev/sda", LoggerType.INFO)
        logger.write_log("Check media presence...", LoggerType.INFO)
        output = Popen(["lsblk","-o", "NAME"], stdout=PIPE)
        check_presence = Popen(["grep", "sda"], stdin=output.stdout, stdout=PIPE).communicate()[0]
        output.stdout.close()
        #Floppy inserted: we need to mount it and run the script with its path
        if len(check_presence) != 0:
            logger.write_log("Device exists on machine.", LoggerType.INFO)
            logger.write_log("Check if media already mounted...", LoggerType.INFO)
            #Avoid throttling
            check_mount = os.path.ismount("/media/floppy")
            if check_mount:
                logger.write_log("Media already mounted. Event ignored.", LoggerType.INFO)
            else:
                logger.write_log("Media not mounted", LoggerType.INFO)
                logger.write_log("Mounting device /dev/sda on /media/floppy.", LoggerType.INFO)
                run(["/usr/bin/systemd-mount", "/dev/sda", "/media/floppy"])
                logger.write_log("Running diskplayer script.", LoggerType.INFO)
                run(["python3", "/home/carole/projects/diskplayer/main.py", "--path", "/media/floppy/diskplayer.contents"])
        else:
            #Floppy removed: we need to stop the playback and unmount the floppy
            logger.write_log("Device does not exist on machine.", LoggerType.INFO)
            logger.write_log("Unmounting device /media/floppy.", LoggerType.INFO)
            run(["/usr/bin/systemd-mount","--umount","/media/floppy"])
            logger.write_log("Stopping diskplayer script.", LoggerType.INFO)
            run(["python3", "/home/carole/projects/diskplayer/main.py", "--pause"])
        logger.write_log("End.", LoggerType.INFO)