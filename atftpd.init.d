#!/bin/sh
#
# atftpd		This shell script takes care of starting and stopping
#				atftpd
# /etc/init.d/atftpd
#
# chkconfig: 345 65 35
# description: atftpd -  Advanced Trivial File Transfer Protocol (TFTP) client
# probe: true
# processname: /usr/sbin/atftpd
# config: /etc/sysconfig/atftpd
# pidfile: /var/run/atftpd/atftpd.pid

### BEGIN INIT INFO
# Provides: atftpd
# Required-Start: $network $syslog
# Required-Stop:  $network $syslog
# Default-Start:  3 5
# Default-Stop:   0 1 2 6
# Description:    launch atftpd server
### END INIT INFO


# Return values acc. to LSB for all commands but status:
# 0 - success
# 1 - generic or unspecified error
# 2 - invalid or excess argument(s)
# 3 - unimplemented feature (e.g. "reload")
# 4 - insufficient privilege
# 5 - program is not installed
# 6 - program is not configured
# 7 - program is not running
# 
# Note that starting an already running service, stopping
# or restarting a not-running service as well as the restart
# with force-reload (in case signalling is not supported) are
# considered a success.
# Source function library.
. /etc/rc.d/init.d/functions

# Source networking configuration.
. /etc/sysconfig/network

# Check that networking is up.
[ "${NETWORKING}" = "no" ] && exit 0

DAEMON="/usr/sbin/atftpd"
NAME=atftpd
DESC="Advanced Trivial FTP server (atftpd)"

if [ ! -x $DAEMON ]; then
	gprintf "Advanced Trivial FTP server, %s is not installed." "$DAEMON"
	# Tell the user this has skipped
	exit 5
fi

# Set default in case of missing sysconfig file
ATFTPD_USE_INETD=yes
ATFTPD_OPTIONS=""
if [ -f /etc/sysconfig/atftpd ]; then
    . /etc/sysconfig/atftpd
fi

if [ "$ATFTPD_USE_INETD" = "yes" ]; then
    exit 0;
fi

case "$1" in
  start)
	gprintf "Starting %s: " "$DESC"
	daemon $DAEMON $ATFTPD_OPTIONS $ATFTPD_DIRECTORY
        RETVAL=$?
	echo
	[ $RETVAL -eq 0 ] && touch /var/lock/subsys/$NAME
	;;
  stop)
	gprintf "Stopping %s:" "$DESC"
	killproc $DAEMON -TERM
	RETVAL=$?
	echo
	[ $RETVAL -eq 0 ] && rm -f /var/lock/subsys/$NAME
	;;
  try-restart)
	## Do a restart only if the service was active before.
	## Note: try-restart is not (yet) part of LSB (as of 1.2)
	$0 status >/dev/null && $0 restart
	;;
  restart|force-reload|reload)
	gprintf "Restarting %s: " "$DESC"
	echo
	$0 stop
	$0 start
	RETVAL=$?
	;;
  status)
	gprintf "Checking for service %s:" "$DESC"

	# Return value is slightly different for the status command:
	# 0 - service running
	# 1 - service dead, but /var/run/  pid  file exists
	# 2 - service dead, but /var/lock/ lock file exists
	# 3 - service not running

	status $DAEMON
	;;
  *)
	gprintf "Usage: %s {start|stop|restart|force-reload|reload|status}\n" "$0"
	exit 1
	;;
esac

exit $RETVAL
