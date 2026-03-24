from clawteam.team.finalizer import TeamFinalizer
from clawteam.team.mailbox import MailboxManager
from clawteam.team.manager import TeamManager
from clawteam.team.models import MessageType
from clawteam.team.tasks import TaskStore


def test_finalizer_sends_reporter_message_once(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAWTEAM_DATA_DIR", str(tmp_path))
    TeamManager.create_team("t1", "leader", "lead1")
    mailbox = MailboxManager("t1")
    mailbox.send(from_agent="reviewer", to="leader", content="最终报告：OK", msg_type=MessageType.message)

    finalizer = TeamFinalizer("t1", mailbox=mailbox)
    r1 = finalizer.finalize(to="leader", reporter="reviewer", allow_takeover=False)
    assert r1.status == "sent"
    assert r1.mode == "reviewer"

    r2 = finalizer.finalize(to="leader", reporter="reviewer", allow_takeover=False)
    assert r2.status == "already_sent"


def test_finalizer_takeover_when_reporter_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAWTEAM_DATA_DIR", str(tmp_path))
    TeamManager.create_team("t2", "leader", "lead2")
    store = TaskStore("t2")
    task = store.create(subject="demo", owner="worker")
    store.update(task.id, status="completed")
    mailbox = MailboxManager("t2")
    mailbox.send(from_agent="worker", to="leader", content="任务已完成：worker摘要", msg_type=MessageType.message)

    finalizer = TeamFinalizer("t2", mailbox=mailbox)
    r = finalizer.finalize(to="leader", reporter="reviewer", allow_takeover=True)
    assert r.status == "sent"
    assert r.mode == "takeover"
    assert "takeover" in r.content
