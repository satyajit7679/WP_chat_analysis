import re
import pandas as pd
import calendar
from typing import Union

def preprocess(data: Union[str, bytes]) -> pd.DataFrame:

    # --- SAME AS BEFORE ---
    if isinstance(data, bytes):
        text = data.decode("utf-8", errors="ignore")
    elif isinstance(data, str):
        if data.lower().endswith(".txt") and "\n" not in data:
            text = open(data, "r", encoding="utf-8", errors="ignore").read()
        else:
            text = data
    else:
        raise TypeError("`data` must be raw text, bytes, or a txt file path")

    pat_chat = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}) - ([^:]+): (.*)$', re.M)
    pat_sys = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}) - (.*)$', re.M)

    rows = []

    for date_str, time_str, sender, msg in pat_chat.findall(text):
        rows.append({
            "date_str": date_str,
            "time_str": time_str,
            "user_message": msg.strip(),
            "user": sender.strip()
        })

    for date_str, time_str, msg in pat_sys.findall(text):
        if ": " not in msg:
            rows.append({
                "date_str": date_str,
                "time_str": time_str,
                "user_message": msg.strip(),
                "user": "group_notification"
            })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # ======== FIXED =============
    df["date"] = pd.to_datetime(df["date_str"], format="%d/%m/%Y", errors="coerce")
    df["time"] = pd.to_datetime(df["time_str"], format="%H:%M", errors="coerce")

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["hour"] = df["time"].dt.hour
    df["minute"] = df["time"].dt.minute

    df["month_name"] = df["month"].apply(lambda x: calendar.month_name[x] if pd.notnull(x) else "")

    df["only_date"] = df["date"].dt.date
    # ==================================

    df = df[[
        "user_message", "date", "time", "user",
        "year", "month", "day", "hour", "minute",
        "month_name", "only_date"
    ]]

    return df
