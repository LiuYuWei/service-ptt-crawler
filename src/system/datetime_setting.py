"""This file is used in setting the feature of datetime."""

# import relation package.
from datetime import datetime


class DatetimeSetting:
    """This class is used in setting the feature of datetime."""

    def __init__(self):
        """Initial some variable"""
        self.time_now = datetime.now()

    def current_time(self, microsecond_enabled=False):
        """now_time: Get the current_time.

        Arguments:
            boolean_microsecond: boolean, want the microsecond or not, default = False.

        Returns:
            now_time: datetime, get the Current time.
        """
        if microsecond_enabled:
            now_time = self.time_now
        else:
            now_time = self.time_now.replace(microsecond=0)
        return now_time

    def strft_time(self, **kwargs):
        """now_time: Get the current_time.

        Arguments:
            time_text: string, the text which is described the time.
            time_format: string, the text which is described the time format.

        Returns:
            time_string: string, the text which is transfer by the specified method.
        """
        if ("time_text" in kwargs) and ("time_format" in kwargs) and ("string_format" in kwargs):
            time_string = datetime.strptime(
                kwargs["time_text"], kwargs["time_format"])
            time_string = datetime.strftime(
                time_string, kwargs["string_format"])
        elif ("time_text" in kwargs) and ("time_format" in kwargs):
            time_string = datetime.strptime(
                kwargs["time_text"], kwargs["time_format"]).isoformat()
        elif "string_format" in kwargs:
            time_string = datetime.strftime(
                self.current_time(), kwargs["string_format"])
        else:
            time_string = self.current_time().isoformat()
        return time_string
