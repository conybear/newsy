from datetime import datetime, timezone, timedelta
import pytz

def get_current_week() -> str:
    """Get current week in ISO format (YYYY-WXX)"""
    # Use Eastern Time for deadline calculations
    et = pytz.timezone('US/Eastern')
    now_et = datetime.now(et)
    
    # Get ISO week
    year, week, _ = now_et.isocalendar()
    return f"{year}-W{week:02d}"

def get_week_deadline(week_str: str) -> datetime:
    """Get Monday 11:59 PM ET deadline for a given week"""
    year, week = week_str.split('-W')
    year, week = int(year), int(week)
    
    # Find Monday of the week
    jan1 = datetime(year, 1, 1)
    jan1_weekday = jan1.weekday()
    
    # Calculate days to first Monday
    days_to_first_monday = (7 - jan1_weekday) % 7
    first_monday = jan1 + timedelta(days=days_to_first_monday)
    
    # Add weeks to get to our target week
    target_monday = first_monday + timedelta(weeks=week-1)
    
    # Set to 11:59 PM ET
    et = pytz.timezone('US/Eastern')
    deadline = et.localize(target_monday.replace(hour=23, minute=59, second=59))
    
    return deadline

def get_publication_time(week_str: str) -> datetime:
    """Get Tuesday 8:00 AM ET publication time for a given week"""
    deadline = get_week_deadline(week_str)
    # Add 8 hours and 1 minute to get to Tuesday 8:00 AM
    return deadline + timedelta(hours=8, minutes=1)

def is_submission_open(week_str: str = None) -> bool:
    """Check if submissions are still open for the current/given week"""
    if week_str is None:
        week_str = get_current_week()
    
    deadline = get_week_deadline(week_str)
    et = pytz.timezone('US/Eastern')
    now_et = datetime.now(et)
    
    return now_et < deadline

def is_published(week_str: str = None) -> bool:
    """Check if the newspaper for the current/given week should be published"""
    if week_str is None:
        week_str = get_current_week()
    
    pub_time = get_publication_time(week_str)
    et = pytz.timezone('US/Eastern')
    now_et = datetime.now(et)
    
    return now_et >= pub_time