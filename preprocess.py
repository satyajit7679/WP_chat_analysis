import re
import pandas as pd
from typing import Union

def preprocess(data: Union[str, bytes]) -> pd.DataFrame:

    # 0) Normalize input -------------------------------------------------------
    if isinstance(data, bytes):
        text = data.decode("utf-8", errors="ignore")
    elif isinstance(data, str):
        # If file path is provided
        if data.lower().endswith(".txt") and "\n" not in data:
            text = open(data, "r", encoding="utf-8", errors="ignore").read()
        else:
            text = data
    else:
        raise TypeError("`data` must be raw text, bytes, or a txt file path")

    # Chat messages with sender
    pat_chat = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}) - ([^:]+): (.*)$',
        re.M
    )

    # Group notifications (no "Sender:")
    pat_sys = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}) - (.*)$',
        re.M
    )

    rows = []

    # ✅ Normal messages
    for date_str, time_str, sender, msg in pat_chat.findall(text):
        rows.append({
            "date_str": date_str,
            "time_str": time_str,
            "user_message": msg.strip(),
            "user": sender.strip()
        })

    # ✅ Group notifications
    for date_str, time_str, msg in pat_sys.findall(text):
        # Avoid double counting messages that matched above
        if ": " not in msg:   # confirm system line
            rows.append({
                "date_str": date_str,
                "time_str": time_str,
                "user_message": msg.strip(),
                "user": "group_notification"
            })

    if not rows:
        return pd.DataFrame(columns=[
            "user_message","date","time","user","year","month","day","hour","minute"
        ])

    df = pd.DataFrame(rows)

    # ---------------------------------------------
    # Date & Time
    # ---------------------------------------------
    df["date"] = pd.to_datetime(df["date_str"], format="%d/%m/%Y", errors="coerce").dt.date
    df["time"] = pd.to_datetime(df["time_str"], format="%H:%M", errors="coerce")

    # Extract components
    df["year"] = pd.to_datetime(df["date"], errors="coerce").dt.year
    df["month"] = pd.to_datetime(df["date"], errors="coerce").dt.month
    df["day"] = pd.to_datetime(df["date"], errors="coerce").dt.day
    df["hour"] = df["time"].dt.hour
    df["minute"] = df["time"].dt.minute

    # ---------------------------------------------
    # Final Columns ONLY
    # ---------------------------------------------
    df = df[["user_message", "date", "time", "user", "year", "month", "day", "hour", "minute"]]

    return df
