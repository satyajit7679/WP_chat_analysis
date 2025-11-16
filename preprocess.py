# import re
# import pandas as pd
# import calendar
# from typing import Union
#
# def preprocess(data: Union[str, bytes]) -> pd.DataFrame:
#
#     # --- SAME AS BEFORE ---
#     if isinstance(data, bytes):
#         text = data.decode("utf-8", errors="ignore")
#     elif isinstance(data, str):
#         if data.lower().endswith(".txt") and "\n" not in data:
#             text = open(data, "r", encoding="utf-8", errors="ignore").read()
#         else:
#             text = data
#     else:
#         raise TypeError("`data` must be raw text, bytes, or a txt file path")
#
#     pat_chat = re.compile(
#         r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}) - ([^:]+): (.*)$', re.M)
#     pat_sys = re.compile(
#         r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}) - (.*)$', re.M)
#
#     rows = []
#
#     for date_str, time_str, sender, msg in pat_chat.findall(text):
#         rows.append({
#             "date_str": date_str,
#             "time_str": time_str,
#             "user_message": msg.strip(),
#             "user": sender.strip()
#         })
#
#     for date_str, time_str, msg in pat_sys.findall(text):
#         if ": " not in msg:
#             rows.append({
#                 "date_str": date_str,
#                 "time_str": time_str,
#                 "user_message": msg.strip(),
#                 "user": "group_notification"
#             })
#
#     if not rows:
#         return pd.DataFrame()
#
#     df = pd.DataFrame(rows)
#
#     # ======== FIXED =============
#     df["date"] = pd.to_datetime(df["date_str"], format="%d/%m/%Y", errors="coerce")
#     df["time"] = pd.to_datetime(df["time_str"], format="%H:%M", errors="coerce")
#
#     df["year"] = df["date"].dt.year
#     df["month"] = df["date"].dt.month
#     df["day"] = df["date"].dt.day
#     df['day_name'] = df['day_name'] = df['date'].dt.day_name()
#     df["hour"] = df["time"].dt.hour
#     df["minute"] = df["time"].dt.minute
#     df["month_name"] = df["month"].apply(lambda x: calendar.month_name[x] if pd.notnull(x) else "")
#     df["only_date"] = df["date"].dt.date
#     # ==================================
#
#     df = df[[
#         "user_message", "date", "time", "user",
#         "year", "month", "day", "hour", "minute",
#         "month_name", "only_date","day_name"
#     ]]
#
#     return df


import re
import pandas as pd
import calendar
from typing import Union
from datetime import datetime

def preprocess(data: Union[str, bytes]) -> pd.DataFrame:

    # --- READ DATA ---
    if isinstance(data, bytes):
        text = data.decode("utf-8", errors="ignore")
    elif isinstance(data, str):
        if data.lower().endswith(".txt") and "\n" not in data:
            text = open(data, "r", encoding="utf-8", errors="ignore").read()
        else:
            text = data
    else:
        raise TypeError("`data` must be raw text, bytes, or a txt file path")

    # REGEX (supports 12-hour + AM/PM + 24-hour)
    pat_chat = re.compile(
        r'^(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}),\s+(\d{1,2}:\d{2}(?:\s?[APMapm]{2})?) - ([^:]+): (.*)$',
        re.M
    )

    pat_sys = re.compile(
        r'^(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}),\s+(\d{1,2}:\d{2}(?:\s?[APMapm]{2})?) - (.*)$',
        re.M
    )

    rows = []

    # CHAT MESSAGES
    for date_str, time_str, sender, msg in pat_chat.findall(text):
        rows.append({
            "date_str": date_str.strip(),
            "time_str": time_str.strip(),
            "user": sender.strip(),
            "user_message": msg.strip()
        })

    # SYSTEM MESSAGES
    for date_str, time_str, msg in pat_sys.findall(text):
        if ": " not in msg:
            rows.append({
                "date_str": date_str.strip(),
                "time_str": time_str.strip(),
                "user": "group_notification",
                "user_message": msg.strip()
            })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # ============================================
    #        DATE PARSER (MULTI-FORMAT)
    # ============================================
    def parse_date(d):
        d = d.strip()

        formats = [
            "%d/%m/%Y", "%d/%m/%y",
            "%m/%d/%Y", "%m/%d/%y",
            "%d-%m-%Y", "%d-%m-%y",
            "%m-%d-%Y", "%m-%d-%y",
            "%d.%m.%Y", "%d.%m.%y"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(d, fmt).date()
            except:
                pass

        return pd.NaT  # Avoid crash

    # ============================================
    #        TIME PARSER (12/24 AUTO-DETECT)
    # ============================================
    def parse_time(t):
        t = t.strip().upper()

        # 12-hour with AM/PM
        if "AM" in t or "PM" in t:
            fixes = [
                "%I:%M %p",
                "%I:%M%p",
                "%I.%M %p"
            ]
            for fmt in fixes:
                try:
                    return datetime.strptime(t, fmt).time()
                except:
                    pass

        # 24 hour formats
        fixes_24 = ["%H:%M", "%H.%M"]

        for fmt in fixes_24:
            try:
                return datetime.strptime(t, fmt).time()
            except:
                pass

        return pd.NaT

    # APPLY PARSERS
    df["date"] = df["date_str"].apply(parse_date)
    df["time"] = df["time_str"].apply(parse_time)

    # EXTRA FIELDS
    df["year"] = df["date"].apply(lambda x: x.year if pd.notnull(x) else None)
    df["month"] = df["date"].apply(lambda x: x.month if pd.notnull(x) else None)
    df["day"] = df["date"].apply(lambda x: x.day if pd.notnull(x) else None)
    df["day_name"] = df["date"].apply(lambda x: x.strftime("%A") if pd.notnull(x) else "")
    df["hour"] = df["time"].apply(lambda x: x.hour if pd.notnull(x) else None)
    df["minute"] = df["time"].apply(lambda x: x.minute if pd.notnull(x) else None)
    df["month_name"] = df["month"].apply(lambda x: calendar.month_name[x] if pd.notnull(x) else "")
    df["only_date"] = df["date"]

    # FINAL ORDER
    df = df[
        [
            "user_message", "date", "time", "user",
            "year", "month", "day", "hour", "minute",
            "month_name", "only_date", "day_name"
        ]
    ]

    return df
