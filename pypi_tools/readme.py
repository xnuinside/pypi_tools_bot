from pypi_tools import __version__

current_version = f"Current pypi_tools_bot version: {__version__}\n"

help_text = "Commands: \n\n" \
            "- <b>/search</b>. You can use command <i><b>/search</b></i> " \
            "to find any package on PyPi and <i><b>/search:detailed</b></i> "\
            "if you want more detailed info.\n " \
            ">>> Example: <i><b>/search aiohttp</b></i> \n\n" \
            "- <b>/stats</b>. Use <i><b>/stats</b></i> command to get download statistics for Python Package. \n" \
            ">>> Example:  <i><b>/stats gino</b></i> \n" \
            "You can setup for how many days you want to have statistic with defining days numbers after command.\n" \
            ">>> Example: <i><b>/stats:10 gino</b></i> . Bot will send to you download statistic for 10 days. \n\n" \
            "-<b>/releases</b> Use this command to get a list with 7 last package releases with dates." \
            ">>> Example: <i><b>/releases aiohttp</b></i> \n\n" \
            "- <b>/plot</b>. Use <i><b>/plot</b></i> command to get plot with download statistics for Python Package. \n" \
            ">>> Example:  <i><b>/plot gino</b></i> \n" \
            "You can setup for how many days you want to have on plot statistic with defining days numbers after command.\n" \
            ">>> Example: <i><b>/plot:10 gino</b></i> . Bot will send to you download statistic for 10 days. \n\n" \
            "-<b>/releases</b> Use this command to get a list with 7 last package releases with dates." \
            ">>> Example: <i><b>/releases aiohttp</b></i> \n\n" \
            "Use <i><b>/releases:full</b></i> to get full list of package releases with dates\n" \
            ">>> Example: <i><b>/releases:full aiohttp</b></i> \n\n" \
            "-<b>/random</b> Commands returns random package from PyPi\n" \
            ">>> Example: <i><b>/random</b></i> \n\n" \
            "-<b>/track package_name</b> Command to add package to your" \
            " track for getting updates about new releases on PyPi. \n" \
            " You will get notification when new release will be able on PyPi. \n" \
            ">>> Example: <i><b>/track flask</b></i> \n" \
            "Use sub-command :stop for remove package from track and stop getting updates about releases \n" \
            ">>> Example: <i><b>/track:stop flask</b></i> \n " \
            "Use sub-command :nodev to get updates without dev releases (versions alpha, beta and etc will be excluded from notifications) \n" \
            ">>> Example: <i><b>/track:nodev flask</b></i> \n """
