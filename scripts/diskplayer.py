
#!/usr/bin/env python3
# /etc/init.d/diskplayer.py
### BEGIN INIT INFO
# Provides:          diskplayer.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

import subprocess

subprocess.run(["python3", "PATH_TO_PROJECT/diskplayer/media_change.py"])