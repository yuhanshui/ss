"""Web application interface for the goal manager."""

from __future__ import annotations

import datetime as dt
from typing import Dict, Iterable, List, Tuple, cast

from flask import Flask, flash, redirect, render_template, request, url_for

from goal_manager import Frequency, Goal, load_data, save_data, frequencies

app = Flask(__name__)
app.secret_key = "dev"  # Needed for flash messages.

FREQUENCIES: Tuple[Frequency, ...] = tuple(frequencies())
FREQUENCY_LABELS = {
    "daily": "每日目标",
    "weekly": "每周目标",
    "monthly": "每月目标",
    "yearly": "每年目标",
}


def _load_goal_models() -> List[Goal]:
    data = load_data()
    return [Goal.from_dict(item) for item in data.get("goals", [])]


def _persist_goal_models(goals: Iterable[Goal]) -> None:
    payload: Dict[str, List[Dict[str, object]]] = {
        "goals": [goal.to_dict() for goal in goals]
    }
    save_data(payload)


def get_goals() -> List[Goal]:
    """Return all goals stored in the JSON file."""
    return _load_goal_models()


def add_goal(name: str, frequency: Frequency) -> Goal:
    """Create a new goal and persist it."""
    if frequency not in FREQUENCIES:
        raise ValueError("频率不在允许范围内。")

    goals = _load_goal_models()
    for goal in goals:
        if goal.name == name and goal.frequency == frequency:
            raise ValueError("该目标已经存在。")

    new_goal = Goal(name=name, frequency=frequency)
    goals.append(new_goal)
    _persist_goal_models(goals)
    return new_goal


def update_status(name: str, frequency: Frequency, done: bool) -> Goal:
    """Update the status of an existing goal for the current period."""
    if frequency not in FREQUENCIES:
        raise ValueError("频率不在允许范围内。")

    goals = _load_goal_models()
    for goal in goals:
        if goal.name == name and goal.frequency == frequency:
            goal.set_status(dt.date.today(), done)
            _persist_goal_models(goals)
            return goal

    raise ValueError("未找到对应的目标。")


@app.get("/")
def index() -> str:
    today = dt.date.today()
    grouped: Dict[Frequency, List[Dict[str, object]]] = {
        freq: [] for freq in FREQUENCIES
    }
    for goal in get_goals():
        grouped.setdefault(goal.frequency, []).append(
            {
                "name": goal.name,
                "status": goal.status_for(today),
            }
        )

    for items in grouped.values():
        items.sort(key=lambda item: item["name"].lower())

    has_goals = any(grouped[freq] for freq in FREQUENCIES)

    status_labels = {
        True: "✅ 已完成",
        False: "❌ 未完成",
        None: "⏳ 未记录",
    }

    return render_template(
        "index.html",
        goals_by_frequency=grouped,
        frequencies=FREQUENCIES,
        frequency_labels=FREQUENCY_LABELS,
        status_labels=status_labels,
        has_goals=has_goals,
    )


@app.post("/add")
def add_goal_route():
    name = request.form.get("name", "").strip()
    frequency = request.form.get("frequency", "daily")

    if not name:
        flash("目标名称不能为空。")
        return redirect(url_for("index"))

    try:
        goal = add_goal(name=name, frequency=cast(Frequency, frequency))
    except ValueError as exc:
        flash(str(exc))
    else:
        flash(f"已添加目标：{goal.name}（{FREQUENCY_LABELS.get(goal.frequency, goal.frequency)}）。")

    return redirect(url_for("index"))


@app.post("/update")
def update_status_route():
    name = request.form.get("name", "").strip()
    frequency = request.form.get("frequency", "")
    done_raw = request.form.get("done", "true").lower()
    done = done_raw in {"1", "true", "yes", "on"}

    if not name:
        flash("缺少目标名称。")
        return redirect(url_for("index"))

    try:
        goal = update_status(
            name=name, frequency=cast(Frequency, frequency), done=done
        )
    except ValueError as exc:
        flash(str(exc))
    else:
        state = "完成" if done else "未完成"
        flash(f"已将「{goal.name}」标记为{state}。")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
