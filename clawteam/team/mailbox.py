"""Mailbox system for inter-agent communication, backed by pluggable Transport."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import time
import uuid

from clawteam.team.models import MessageType, TeamMessage, get_data_dir
from clawteam.transport.base import Transport


def _default_transport(team_name: str) -> Transport:
    """Resolve the transport from env / config, with optional P2P listener binding."""
    import os

    name = os.environ.get("CLAWTEAM_TRANSPORT", "")
    if not name:
        from clawteam.config import load_config
        name = load_config().transport or "file"
    if name == "p2p":
        from clawteam.identity import AgentIdentity
        agent = AgentIdentity.from_env().agent_name
        from clawteam.transport import get_transport
        return get_transport("p2p", team_name=team_name, bind_agent=agent)
    from clawteam.transport import get_transport
    return get_transport("file", team_name=team_name)


class MailboxManager:
    """Mailbox for inter-agent messaging, delegating I/O to a Transport.

    Each message is a JSON file in the recipient's inbox directory:
    ``{data_dir}/teams/{team}/inboxes/{agent}/msg-{timestamp}-{uuid}.json``

    Atomic writes (write tmp then rename) prevent partial reads.
    """

    _RESUME_TRIGGER_PREFIXES = (
        "All tasks completed.",
        "任务已完成：",
        "FINAL:",
        "最终汇总：",
        "RISK REPORT:",
        "风险报告：",
        "Need help:",
        "需要协助：",
        "MEMO:",
        "备忘录：",
        "SECURITY:",
        "安全：",
        "PERFORMANCE:",
        "性能：",
        "ARCHITECTURE:",
        "架构：",
        "SYSTEMS:",
        "系统：",
        "DELIVERY:",
        "交付：",
        "RISK:",
        "风险：",
        "LITERATURE:",
        "文献：",
        "METHODOLOGY:",
        "方法：",
        "RESULTS:",
        "结果：",
        "SIGNAL:",
        "信号：",
    )

    def __init__(self, team_name: str, transport: Transport | None = None):
        self.team_name = team_name
        self._transport = transport or _default_transport(team_name)
        self._events_dir = get_data_dir() / "teams" / team_name / "events"
        self._events_dir.mkdir(parents=True, exist_ok=True)

    def _log_event(self, msg: TeamMessage) -> None:
        """Persist message to event log (never consumed, for history)."""
        ts = int(time.time() * 1000)
        uid = uuid.uuid4().hex[:8]
        path = self._events_dir / f"evt-{ts}-{uid}.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(
            msg.model_dump_json(indent=2, by_alias=True, exclude_none=True),
            encoding="utf-8",
        )
        tmp.rename(path)

    def get_event_log(self, limit: int = 100) -> list[TeamMessage]:
        """Read event log (newest first). Non-destructive."""
        files = sorted(self._events_dir.glob("evt-*.json"), reverse=True)[:limit]
        msgs = []
        for f in files:
            try:
                msgs.append(TeamMessage.model_validate(json.loads(f.read_text("utf-8"))))
            except Exception:
                pass
        return msgs

    def send(
        self,
        from_agent: str,
        to: str,
        content: str | None = None,
        msg_type: MessageType = MessageType.message,
        request_id: str | None = None,
        key: str | None = None,
        proposed_name: str | None = None,
        capabilities: str | None = None,
        feedback: str | None = None,
        reason: str | None = None,
        assigned_name: str | None = None,
        agent_id: str | None = None,
        team_name: str | None = None,
        plan_file: str | None = None,
        summary: str | None = None,
        plan: str | None = None,
        last_task: str | None = None,
        status: str | None = None,
        wake_leader: bool = True,
    ) -> TeamMessage:
        from clawteam.team.manager import TeamManager

        delivery_target = TeamManager.resolve_inbox(self.team_name, to)
        msg = TeamMessage(
            type=msg_type,
            from_agent=from_agent,
            to=to,
            content=content,
            request_id=request_id or uuid.uuid4().hex[:12],
            key=key,
            proposed_name=proposed_name,
            capabilities=capabilities,
            feedback=feedback,
            reason=reason,
            assigned_name=assigned_name,
            agent_id=agent_id,
            team_name=team_name,
            plan_file=plan_file,
            summary=summary,
            plan=plan,
            last_task=last_task,
            status=status,
        )
        data = msg.model_dump_json(indent=2, by_alias=True, exclude_none=True).encode("utf-8")
        self._transport.deliver(delivery_target, data)
        self._log_event(msg)
        if wake_leader:
            self._maybe_wake_leader(msg)
        return msg

    def broadcast(
        self,
        from_agent: str,
        content: str,
        msg_type: MessageType = MessageType.broadcast,
        key: str | None = None,
        exclude: list[str] | None = None,
    ) -> list[TeamMessage]:
        from clawteam.team.manager import TeamManager

        exclude_set = set(exclude or [])
        exclude_set.add(from_agent)
        # Build a mapping from inbox directory name to logical agent name
        # so we can correctly exclude the sender even when inbox names
        # use user-prefixed format (e.g. "alice_worker").
        exclude_inboxes = set()
        for name in exclude_set:
            inbox = TeamManager.resolve_inbox(self.team_name, name)
            exclude_inboxes.add(inbox)
            exclude_inboxes.add(name)  # also exclude by raw name
        messages = []
        for recipient in self._transport.list_recipients():
            if recipient not in exclude_inboxes:
                msg = TeamMessage(
                    type=msg_type,
                    from_agent=from_agent,
                    to=recipient,
                    content=content,
                    key=key,
                )
                data = msg.model_dump_json(
                    indent=2, by_alias=True, exclude_none=True
                ).encode("utf-8")
                self._transport.deliver(recipient, data)
                self._log_event(msg)
                messages.append(msg)
        return messages

    def receive(self, agent_name: str, limit: int = 10) -> list[TeamMessage]:
        """Receive and delete messages from an agent's inbox (FIFO)."""
        raw = self._transport.fetch(agent_name, limit=limit, consume=True)
        return [TeamMessage.model_validate(json.loads(r)) for r in raw]

    def peek(self, agent_name: str) -> list[TeamMessage]:
        """Return pending messages without consuming them."""
        raw = self._transport.fetch(agent_name, consume=False)
        return [TeamMessage.model_validate(json.loads(r)) for r in raw]

    def peek_count(self, agent_name: str) -> int:
        return self._transport.count(agent_name)

    def _maybe_wake_leader(self, msg: TeamMessage) -> None:
        """Best-effort resume for an idle inbox-driven agent when a key team message arrives.

        Generalized fix for template-based swarms where an agent finishes one turn,
        goes idle, and never resumes to consume later inbox messages.
        """
        try:
            if msg.type != MessageType.message:
                return
            if not msg.to:
                return
            content = (msg.content or "").strip()
            if not content:
                return
            if not any(content.startswith(prefix) for prefix in self._RESUME_TRIGGER_PREFIXES):
                return

            from clawteam.spawn.registry import is_agent_alive
            from clawteam.team.tasks import TaskStore

            recipient = msg.to
            if msg.from_agent == recipient:
                return

            # Resume only when the recipient still has unfinished owned work.
            ts = TaskStore(self.team_name)
            recipient_tasks = [
                t for t in ts.list_tasks(owner=recipient)
                if t.status != "completed"
            ]
            if not recipient_tasks:
                return

            prompt = (
                f"New inbox message(s) have arrived for {recipient} in team {self.team_name}. "
                f"Resume now: read pending inbox messages addressed to {recipient}, "
                f"continue your active task(s), and if your work is complete, "
                f"send any required summary/report to the appropriate teammate and mark the relevant task(s) completed via "
                f"'clawteam task update {self.team_name} <task-id> --status completed'."
            )

            from clawteam.spawn.sessions import SessionStore
            session_store = SessionStore(self.team_name)
            session = session_store.load(recipient)
            if session and session.session_id:
                result = subprocess.run(
                    [
                        "openclaw",
                        "agent",
                        "--session-id",
                        session.session_id,
                        "--message",
                        prompt,
                        "--timeout",
                        "120",
                        "--json",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    return

            # If the recipient has no reusable session but has an idle tmux-backed TUI,
            # inject a fresh user turn directly into that pane.
            if is_agent_alive(self.team_name, recipient):
                from clawteam.spawn.registry import get_registry
                info = get_registry(self.team_name).get(recipient, {})
                tmux_target = info.get("tmux_target", "")
                if tmux_target:
                    injected = self._inject_tmux_resume(tmux_target, prompt)
                    if injected:
                        return
                return

            clawteam_bin = os.environ.get("CLAWTEAM_BIN") or shutil.which("clawteam") or "clawteam"
            subprocess.run(
                [
                    clawteam_bin,
                    "spawn",
                    "-t",
                    self.team_name,
                    "-n",
                    recipient,
                    "--agent-type",
                    "member",
                    "--task",
                    prompt,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            return

    def _inject_tmux_resume(self, tmux_target: str, prompt: str) -> bool:
        """Best-effort tmux injection for an alive-but-idle TUI agent.

        We send Escape/Ctrl-C to clear any partial input, paste the new prompt,
        and submit a fresh turn. This is a local fallback for agents that do not
        have a reusable saved session yet.
        """
        try:
            subprocess.run(["tmux", "send-keys", "-t", tmux_target, "Escape"], check=False)
            subprocess.run(["tmux", "send-keys", "-t", tmux_target, "C-c"], check=False)
            subprocess.run(["tmux", "set-buffer", "--", prompt], check=False)
            subprocess.run(["tmux", "paste-buffer", "-t", tmux_target], check=False)
            subprocess.run(["tmux", "send-keys", "-t", tmux_target, "Enter"], check=False)
            return True
        except Exception:
            return False
