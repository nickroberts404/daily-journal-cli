from collections import defaultdict
from datetime import date, timedelta

import typer
from rich import print

from daily_journal_cli.db import database
from daily_journal_cli.util import format_date, string_to_date
from .print_entries import print_entries

today = date.today()


def split_date_range(date_range: str) -> list[date]:
    dates = date_range.split("-")
    if len(dates) != 2:
        print(
            "[red bold]Please provide date range in valid format[/] (example: 05/26/1994-06/01/1994)."
        )
        raise typer.Exit()
    return [string_to_date(d) for d in dates]


def date_range_by_days_ago(days: int) -> list[date]:
    start_date = today - timedelta(days=days - 1)
    return [start_date, today]


def get_range(date_range: str, last_n_days: int) -> list[date]:
    if date_range:
        start, end = split_date_range(date_range)
    else:
        start, end = date_range_by_days_ago(last_n_days)
    return [start, end]


def get_entries_grouped_by_date(start: date, end: date):
    existing_entries = database.get_entries_by_date_range(start, end)
    entries_grouped_by_date = defaultdict(list)
    for entry in existing_entries:
        entries_grouped_by_date[entry.date].append(entry)
    return entries_grouped_by_date


def get_list_of_dates(start: date, end: date) -> list[date]:
    difference_in_days = (end - start).days + 1
    return [start + timedelta(days=x) for x in range(difference_in_days)]


def print_entries_by_date(entries_grouped_by_date, list_of_dates):
    for d in list_of_dates:
        print(format_date(d))
        entries = entries_grouped_by_date[d]
        if len(entries) > 0:
            print_entries(entries)
        else:
            print("[red]No entries[/]")
        print("")  # Would be cool to print a "rule" here, if we switch to rich.console


def view(
    last_n_days: int or None,
    date_range: str or None,
):
    start, end = get_range(date_range, last_n_days)
    entries_grouped_by_date = get_entries_grouped_by_date(start, end)
    list_of_dates = get_list_of_dates(start, end)
    print_entries_by_date(entries_grouped_by_date, list_of_dates)