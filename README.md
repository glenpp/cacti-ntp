# NTP & chronyd Monitoring on Cacti over SNMP

This time looking at NTP, something seldom monitored, but these days becoming increasingly important to ensure that you have a quality sync. In many cases NTP goes un-monitored and people only realize there is a problem when applications that depend on accurate time break, but you can take action long before anything fails.

I'm not going to cover configuration of ntpd or chronyd - out the box it should be working with most distros and about all you may want to do is add a local "preferred" server (possibly removing public ones).

## Collecting data & snmpd Extensions

When you have ntpd running you can query it with the ntpq command in various ways and that's pretty much all I do for this one. You will need to add in the extension script as per snmpd.conf.cacti-ntp in /etc/snmp/snmpd.conf

If you have chronyd running you can query it with the chronyc command in similar ways. You will need to add the extension script as per snmpd.conf.cacti-chrony in /etc/snmp/snmpd.conf

Grab the extension script ntp-stats or chrony\_stats.py below and put it in an appropriate place (I use /etc/snmp/), adjusting the config above to match.

Restart snmpd and you should be able to query the new OIDs.

## Cacti

Then you need to import the Cacti template cacti_host_template_ntp_monitor.xml or cacti_host_template_chrony_ntp_monitor.xml to go with these and create the graphs in Cacti.

