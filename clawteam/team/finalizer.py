"""Final report orchestration for teams.

Provides a small, productizable layer on top of task waiting:
- Persist whether a final report has been sent (idempotency)
- Extract a reviewer/reporter message from the team event log
- Synthesize a takeover report when reviewer output is missing
- Send the final report exactly once to a chosen inbox
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from clawteam.team.mailbox import MailboxManager
from clawteam.team.models import MessageType, TeamMessage, get_data_dir
from clawteam.team.tasks import TaskStore


@dataclass
class FinalReportState:
    status: str = "pending"  # pending|sent
    mode: str = ""  # reviewer|takeover
    report_id: str = ""
    content: str = ""
    sent_at: str = ""
    source_agent: str = ""
    delivered_to: str = ""


@dataclass
class FinalizeResult:
    status: str  # sent|already_sent|missing
    mode: str = ""
    content: str = ""
    report_id: str = ""
    delivered_to: str = ""


class TeamFinalizer:
    def __init__(self, team_name: str, mailbox: MailboxManager | None = None):
        self.team_name = team_name
        self.mailbox = mailbox or MailboxManager(team_name)
        self.task_store = TaskStore(team_name)

    def state_path(self) -> Path:
        path = get_data_dir() / "teams" / self.team_name / "final_report.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def load_state(self) -> FinalReportState:
        path = self.state_path()
        if not path.exists():
            return FinalReportState()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return FinalReportState(**data)
        except Exception:
            return FinalReportState()

    def save_state(self, state: FinalReportState) -> None:
        path = self.state_path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.rename(path)

    def get_reporter_message(self, reporter: str) -> TeamMessage | None:
        events = self.mailbox.get_event_log(limit=500)
        for msg in events:
            if msg.from_agent == reporter and msg.type == MessageType.message and (msg.content or "").strip():
                return msg
        return None

    def synthesize_takeover_report(self, max_messages: int = 10) -> str:
        tasks = self.task_store.list_tasks()
        completed = sum(1 for t in tasks if t.status.value == "completed")
        total = len(tasks)
        messages = []
        for msg in self.mailbox.get_event_log(limit=100):
            content = (msg.content or "").strip()
            if msg.type == MessageType.message and content:
                messages.append(f"- {msg.from_agent}: {content}")
            if len(messages) >= max_messages:
                break
        joined = "\n".join(reversed(messages)) if messages else "- 无可用消息摘要"
        return (
            f"[takeover] 团队终稿：当前任务完成度 {completed}/{total}。"
            f" 由于指定汇总代理未按时产出终稿，系统已接管汇总。\n"
            f"已收集到的关键信息：\n{joined}"
        )

    def finalize(
        self,
        *,
        to: str,
        from_agent: str = "finalizer",
        reporter: str = "reviewer",
        allow_takeover: bool = False,
    ) -> FinalizeResult:
        state = self.load_state()
        if state.status == "sent" and state.report_id:
            return FinalizeResult(
                status="already_sent",
                mode=state.mode,
                content=state.content,
                report_id=state.report_id,
                delivered_to=state.delivered_to,
            )

        msg = self.get_reporter_message(reporter)
        mode = "reviewer"
        content = ""
        source_agent = reporter
        if msg and (msg.content or "").strip():
            content = (msg.content or "").strip()
        elif allow_takeover:
            mode = "takeover"
            source_agent = from_agent
            content = self.synthesize_takeover_report()
        else:
            return FinalizeResult(status="missing")

        report_id = uuid.uuid4().hex[:12]
        self.mailbox.send(
            from_agent=from_agent,
            to=to,
            content=content,
            msg_type=MessageType.message,
            wake_leader=True,
        )
        state = FinalReportState(
            status="sent",
            mode=mode,
            report_id=report_id,
            content=content,
            sent_at=datetime.now(timezone.utc).isoformat(),
            source_agent=source_agent,
            delivered_to=to,
        )
        self.save_state(state)
        return FinalizeResult(
            status="sent",
            mode=mode,
            content=content,
            report_id=report_id,
            delivered_to=to,
        )
