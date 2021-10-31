Configuration
=============

Basics
------

Besides a reboot, you also need to configure the program. The configuration files
use the json-format. The following files are available:

  - `/etc/pi-e-ink-daily.json`: user-specific configuration
  - `/etc/pi-e-ink-daily.defaults.json`: defaults for the framework-program
  - `/etc/pi-e-ink-daily.CalContentProvider.json`: defaults for the calendar-display
  - `/etc/pi-e-ink-daily.WeatherContentProvider.json`: defaults for the
    weather-forecast

Typical settings are fonts and fontsizes, colors, usernames and passwords.

To configure settings, copy the relevant entries from one of the files
`pi-e-ink-daily.?????.json` to the file `pi-e-ink-daily.json'. Never change one
of the other files, since an update will overwrite the changes.

Edit the file with a simple editor, the variable-names should be
self-explanatory. Depending on your system, you might need to edit the
paths to the fonts.


Framework-Settings
------------------

To select the *content-provider*, you have to set the property:

    "content_provider" : "CalContentProvider",

Valid values currently are `CalContentProvider` (displays agenda-items
from one or more calendars) and `WeatherContentProvider` (displays
a weather-forecast based on OpenWeatherMap data).

To configure the title, use the *TITLE*-setting:

    "TITLE" : "",

If this variable is the empty string, the title will show the current month.
Otherwise, it will be interpreted as a strftime-spec (note that a simple
string is a valid strftime-spec). Please read the python3-documentation
regarding the format and placeholders of a strftime-spec.

There are two settings which are only necessary for desktop-simulation:

    "WIDTH"        : 400,
    "HEIGHT"       : 300,

If the program detects a real inky, it will use the physical dimensions.

To configure the __shutdown-behavior__, set the following variables:

    "auto_shutdown"        : 0,
    "no_shutdown_on_error" : 0,

After initial testing, you would set the first variable to `1` to enable
automatic shutdown (except if you are running from a wall-plug and don't
need to shutdown to save battery-power).

If the second variable is set, the system will stay up even if there are
errors during the update, e.g. because the network is not available. Since
this will drain your battery, this setting is only recommended for debugging.


Calender-Settings
-----------------

The program supports multiple calendars, the following settings are necessary
for every configured calendar (see `/etc/pi-e-ink-daily.CalContentProvider.json`):

    "dav_url"      : "https://example.com/caldav.php",
    "dav_user"     : "somebody",
    "dav_pw"       : "somebodies_password",
    "cal_name"     : "mycal",
    "cal_color"    : "white"

Using a different color than white or gray for the background of the agenda-entry
(`cal_color`) is not recommended for a wHat.


Weather-Forecast Settings
-------------------------

Besides some fonts, there are mainly three settings:

    "owm_latitude"  : 48.135125,
    "owm_longitude" : 11.581981,
    "owm_apikey"    : "undef"

Query the latitude and longitude of your preferred location using Wikipedia
or Google-Maps.

Head to <https://openweathermap.org/api> to request your own API-key. Besides
paid plans there is a free option which is enough to update your e-ink every
two minutes. Since the weather-data itself is only updated every 10 minutes, the
free plan is all you need.
