"""
Market schedule utilities for US stock market.

Handles market hours, holidays, early closes, and trading day calculations.
All times are in US/Eastern timezone.
"""
from datetime import datetime, time as dtime, timedelta
import pytz

# US/Eastern timezone
EAST = pytz.timezone("US/Eastern")


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> datetime.date:
    """Find the nth occurrence of a weekday in a month.
    
    Args:
        year: Year
        month: Month (1-12)
        weekday: Weekday (Monday=0 .. Sunday=6)
        n: Occurrence number (1st, 2nd, etc.)
    
    Returns:
        Date of the nth weekday
    """
    d = datetime(year, month, 1).date()
    first_weekday = d.weekday()
    delta_days = (weekday - first_weekday) % 7
    day = 1 + delta_days + (n - 1) * 7
    return datetime(year, month, day).date()


def _last_weekday(year: int, month: int, weekday: int) -> datetime.date:
    """Find the last occurrence of a weekday in a month.
    
    Args:
        year: Year
        month: Month (1-12)
        weekday: Weekday (Monday=0 .. Sunday=6)
    
    Returns:
        Date of the last weekday in the month
    """
    from calendar import monthrange
    last_day = monthrange(year, month)[1]
    d = datetime(year, month, last_day).date()
    delta = (d.weekday() - weekday) % 7
    return d - timedelta(days=delta)


def _easter_date(year: int) -> datetime.date:
    """Calculate Easter Sunday date using the Anonymous Gregorian algorithm.
    
    Args:
        year: Year to calculate Easter for
    
    Returns:
        Date of Easter Sunday
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day).date()


def is_market_holiday(d: datetime.date) -> bool:
    """Check if a given date is a US stock market holiday.
    
    Args:
        d: Date to check
    
    Returns:
        True if the date is a market holiday
    """
    year = d.year
    holidays = set()

    # New Year's Day (observed)
    ny = datetime(year, 1, 1).date()
    if ny.weekday() == 5:  # Saturday -> observed Friday
        holidays.add(ny - timedelta(days=1))
    elif ny.weekday() == 6:  # Sunday -> observed Monday
        holidays.add(ny + timedelta(days=1))
    else:
        holidays.add(ny)

    # Martin Luther King Jr. Day: third Monday in January
    holidays.add(_nth_weekday(year, 1, 0, 3))

    # Presidents' Day (Washington): third Monday in February
    holidays.add(_nth_weekday(year, 2, 0, 3))

    # Good Friday: Friday before Easter
    eas = _easter_date(year)
    holidays.add(eas - timedelta(days=2))

    # Memorial Day: last Monday in May
    holidays.add(_last_weekday(year, 5, 0))

    # Juneteenth: June 19 (observed)
    j = datetime(year, 6, 19).date()
    if j.weekday() == 5:
        holidays.add(j - timedelta(days=1))
    elif j.weekday() == 6:
        holidays.add(j + timedelta(days=1))
    else:
        holidays.add(j)

    # Independence Day: July 4 (observed)
    ind = datetime(year, 7, 4).date()
    if ind.weekday() == 5:
        holidays.add(ind - timedelta(days=1))
    elif ind.weekday() == 6:
        holidays.add(ind + timedelta(days=1))
    else:
        holidays.add(ind)

    # Labor Day: first Monday in September
    holidays.add(_nth_weekday(year, 9, 0, 1))

    # Thanksgiving: fourth Thursday in November
    holidays.add(_nth_weekday(year, 11, 3, 4))

    # Christmas Day: Dec 25 (observed)
    x = datetime(year, 12, 25).date()
    if x.weekday() == 5:
        holidays.add(x - timedelta(days=1))
    elif x.weekday() == 6:
        holidays.add(x + timedelta(days=1))
    else:
        holidays.add(x)

    return d in holidays


def is_early_close(d: datetime.date) -> bool:
    """Check if a given date has early market close at 13:00 ET.
    
    Early close days:
    - The day before Independence Day (if July 4 is a weekday)
    - The day after Thanksgiving (Black Friday)
    - Christmas Eve (Dec 24)
    
    Args:
        d: Date to check
    
    Returns:
        True if the market closes early on this date
    """
    year = d.year
    
    # Day before Independence Day
    ind = datetime(year, 7, 4).date()
    day_before_ind = ind - timedelta(days=1)

    # Day after Thanksgiving: Thanksgiving is fourth Thursday in November
    thanks = _nth_weekday(year, 11, 3, 4)
    day_after_thanks = thanks + timedelta(days=1)

    # Christmas Eve
    xmas_eve = datetime(year, 12, 24).date()

    return d in (day_before_ind, day_after_thanks, xmas_eve)


def in_market_hours(now=None):
    """Check if the current time is during market hours.
    
    Market hours: 9:30 AM - 4:00 PM ET (or 1:00 PM ET on early close days)
    
    Args:
        now: Optional datetime to check. If None, uses current time.
    
    Returns:
        True if the market is currently open
    """
    now = now or datetime.now(EAST)
    
    # Build aware datetimes in US/Eastern correctly using localize
    start_naive = datetime.combine(now.date(), dtime(hour=9, minute=30))
    
    # Use early close at 13:00 on certain days
    if is_early_close(now.date()):
        end_naive = datetime.combine(now.date(), dtime(hour=13, minute=0))
    else:
        end_naive = datetime.combine(now.date(), dtime(hour=16, minute=0))
    
    start = EAST.localize(start_naive)
    end = EAST.localize(end_naive)
    
    return start <= now <= end


def next_trading_day_start(now: datetime) -> datetime:
    """Find the next trading day market open time.
    
    Args:
        now: Current datetime (should be timezone-aware in EAST)
    
    Returns:
        Datetime of the next market open (9:30 AM ET)
    """
    cur_date = now.date()
    candidate = cur_date
    
    # Start searching from today if before open, else next day
    start_naive = datetime.combine(candidate, dtime(hour=9, minute=30))
    start_dt = EAST.localize(start_naive)
    if now >= start_dt:
        candidate = candidate + timedelta(days=1)

    # Find next day that is Mon-Fri and not a market holiday
    while True:
        if candidate.weekday() >= 5 or is_market_holiday(candidate):
            candidate = candidate + timedelta(days=1)
            continue
        # Found trading day
        next_open_naive = datetime.combine(candidate, dtime(hour=9, minute=30))
        return EAST.localize(next_open_naive)


def is_trading_day(d: datetime.date) -> bool:
    """Check if a given date is a trading day (not weekend or holiday).
    
    Args:
        d: Date to check
    
    Returns:
        True if the date is a trading day
    """
    return d.weekday() < 5 and not is_market_holiday(d)


def get_market_hours(d: datetime.date) -> tuple[dtime, dtime]:
    """Get market open and close times for a given date.
    
    Args:
        d: Date to get market hours for
    
    Returns:
        Tuple of (open_time, close_time) as time objects
    """
    open_time = dtime(hour=9, minute=30)
    
    if is_early_close(d):
        close_time = dtime(hour=13, minute=0)
    else:
        close_time = dtime(hour=16, minute=0)
    
    return open_time, close_time