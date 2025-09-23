#!/usr/bin/env python3
"""Simple goal manager for daily, weekly, monthly, and yearly targets.

The script stores progress in a JSON file under the user's application-data
directory so that history is preserved between runs. Users can add goals and
run a daily reminder that asks whether each goal has been completed for the
current period.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
import sys
from typing import Dict, Iterable, List, Literal, Optional

Frequency = Literal["daily", "weekly", "monthly", "yearly"]


APP_NAME = "GoalManager"
DATA_ENV_VAR = "GOAL_MANAGER_DATA"


def _resolve_data_dir() -> Path:
    override = os.getenv(DATA_ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()

    if sys.platform.startswith("win"):
        base = os.getenv("APPDATA") or os.getenv("LOCALAPPDATA")
        if base:
            base_path = Path(base)
        else:
            base_path = Path.home() / "AppData" / "Local"
        return base_path / APP_NAME

    xdg_home = os.getenv("XDG_DATA_HOME")
    if xdg_home:
        base_path = Path(xdg_home)
    else:
        base_path = Path.home() / ".local" / "share"
    return base_path / APP_NAME.lower()


DATA_DIR = _resolve_data_dir()
DATA_FILE = DATA_DIR / "goal_manager.json"


def load_data() -> Dict[str, List[Dict[str, object]]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"goals": []}


def save_data(data: Dict[str, List[Dict[str, object]]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def period_key(date: dt.date, frequency: Frequency) -> str:
    if frequency == "daily":
        return date.strftime("%Y-%m-%d")
    if frequency == "weekly":
        year, week, _ = date.isocalendar()
        return f"{year}-W{week:02d}"
    if frequency == "monthly":
        return date.strftime("%Y-%m")
    if frequency == "yearly":
        return date.strftime("%Y")
    raise ValueError(f"Unsupported frequency: {frequency}")


def frequencies() -> Iterable[Frequency]:
    yield from ("daily", "weekly", "monthly", "yearly")


@dataclass
class Goal:
    name: str
    frequency: Frequency
    history: Dict[str, Dict[str, object]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "Goal":
        return cls(
            name=str(payload["name"]),
            frequency=payload["frequency"],
            history=payload.get("history", {}),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "frequency": self.frequency,
            "history": self.history,
        }

    def status_for(self, date: dt.date) -> Optional[bool]:
        record = self.history.get(period_key(date, self.frequency))
        return None if record is None else bool(record["done"])

    def set_status(self, date: dt.date, done: bool) -> None:
        self.history[period_key(date, self.frequency)] = {
            "done": done,
            "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        }


def find_goal(goals: Iterable[Goal], name: str, frequency: Frequency) -> Goal:
    for goal in goals:
        if goal.name == name and goal.frequency == frequency:
            return goal
    raise SystemExit(f"Goal '{name}' ({frequency}) not found.")


def add_goal(data: Dict[str, List[Dict[str, object]]], name: str, frequency: Frequency) -> None:
    goals = [Goal.from_dict(item) for item in data.get("goals", [])]
    for goal in goals:
        if goal.name == name and goal.frequency == frequency:
            raise SystemExit("Goal already exists.")
    goals.append(Goal(name=name, frequency=frequency))
    data["goals"] = [goal.to_dict() for goal in goals]
    save_data(data)
    print(f"Added {frequency} goal: {name}")


def list_goals(data: Dict[str, List[Dict[str, object]]]) -> None:
    goals = [Goal.from_dict(item) for item in data.get("goals", [])]
    if not goals:
        print("No goals defined yet. Use the 'add' command to create one.")
        return

    today = dt.date.today()
    print("Current goals and today's status:\n")
    for freq in frequencies():
        freq_goals = [goal for goal in goals if goal.frequency == freq]
        if not freq_goals:
            continue
        print(f"[{freq.capitalize()} goals]")
        for goal in freq_goals:
            status = goal.status_for(today)
            indicator = {
                True: "✅ Done",
                False: "❌ Not done",
                None: "⏳ Pending",
            }[status]
            print(f"- {goal.name}: {indicator}")
        print()


def check_goal(
    data: Dict[str, List[Dict[str, object]]],
    name: str,
    frequency: Frequency,
    done: bool,
    date: Optional[dt.date] = None,
) -> None:
    goals = [Goal.from_dict(item) for item in data.get("goals", [])]
    goal = find_goal(goals, name=name, frequency=frequency)
    goal.set_status(date or dt.date.today(), done)
    data["goals"] = [item.to_dict() for item in goals]
    save_data(data)
    print(f"Marked '{goal.name}' ({goal.frequency}) as {'done' if done else 'not done'}.")


def prompt_yes_no(prompt: str) -> Optional[bool]:
    while True:
        response = input(prompt).strip().lower()
        if not response:
            return None
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            return False
        print("Please enter 'y' for yes, 'n' for no, or press Enter to skip.")


def remind(data: Dict[str, List[Dict[str, object]]]) -> None:
    goals = [Goal.from_dict(item) for item in data.get("goals", [])]
    if not goals:
        print("No goals to remind you about. Add one with the 'add' command first.")
        return

    today = dt.date.today()
    print("Daily goal reminder. Press Enter to leave a goal unchanged.")
    for goal in goals:
        status = goal.status_for(today)
        status_text = {
            True: "already marked as done",
            False: "currently marked as not done",
            None: "not yet recorded",
        }[status]
        answer = prompt_yes_no(
            f"Did you finish '{goal.name}' ({goal.frequency}, {status_text})? [y/n/Enter] "
        )
        if answer is None:
            continue
        goal.set_status(today, answer)

    data["goals"] = [goal.to_dict() for goal in goals]
    save_data(data)
    print("Reminder complete. Great job staying on track!")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Personal goal manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new goal")
    add_parser.add_argument("name", help="Name of the goal")
    add_parser.add_argument(
        "--frequency",
        choices=list(frequencies()),
        default="daily",
        help="How often the goal repeats",
    )

    list_parser = subparsers.add_parser("list", help="Show goals and their status")
    list_parser

    check_parser = subparsers.add_parser("check", help="Manually mark a goal done/not done")
    check_parser.add_argument("name", help="Name of the goal")
    check_parser.add_argument(
        "--frequency",
        choices=list(frequencies()),
        default="daily",
        help="Frequency of the goal",
    )
    status_group = check_parser.add_mutually_exclusive_group(required=True)
    status_group.add_argument("--done", action="store_true", help="Mark as done")
    status_group.add_argument("--not-done", action="store_true", help="Mark as not done")

    subparsers.add_parser("remind", help="Run the interactive daily reminder")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = load_data()

    if args.command == "add":
        add_goal(data, name=args.name, frequency=args.frequency)
    elif args.command == "list":
        list_goals(data)
    elif args.command == "check":
        done = True if args.done else False
        check_goal(data, name=args.name, frequency=args.frequency, done=done)
    elif args.command == "remind":
        remind(data)
    else:
        raise SystemExit(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
