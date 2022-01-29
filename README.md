# mailalive
Scripts to monitor mail delivery using Nagios / Icinga

## Usage
* Either manually replace the variables and rename to `mailalive_cron.sh` or use the provided `mailalive_cron.sh.epp` as a EPP template in puppet and provide a `vars` hash.
* Ensure the cron script is running hourly
* Add the mailalive.py script as a command and service check in Nagios / Icinga.
