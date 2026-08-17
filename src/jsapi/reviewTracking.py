from ..utils.JSCallable import JSCallable
from ..utils.debugLog import log

from aqt import mw, gui_hooks
from anki.consts import (
    QUEUE_TYPE_NEW,
    QUEUE_TYPE_LRN,
    QUEUE_TYPE_DAY_LEARN_RELEARN,
    QUEUE_TYPE_REV,
)

# Live feed of true review events, drained by the JS side every card. Not
# meant to survive an Anki restart - process-lifetime only, unlike
# ankiPersistentStorage.py which is now backed by collection config.
_pending = None
_seq = 0
_events = []


# process lifecycle-bound tracking variable for javascript
_jsLastSeenSeq = 0


@JSCallable
def getLastSeenSeq():
    return _jsLastSeenSeq


@JSCallable
def setLastSeenSeq(newSeq):
    global _jsLastSeenSeq
    _jsLastSeenSeq = newSeq


def _on_will_answer_card(ease_tuple, reviewer, card):
    # Runs before scheduling, so card.queue/type still reflect the pre-answer
    # state - captured here since reviewer_did_answer_card may run after
    # card.load() has already reloaded the post-answer state.
    global _pending
    _pending = {
        "cardId": card.id,
        "queue": card.queue,
        "ease": ease_tuple[1],
    }
    return ease_tuple


def _on_did_answer_card(reviewer, card, ease):
    global _pending, _seq
    if _pending is None or _pending["cardId"] != card.id:
        # Answer was vetoed/rerouted between the two hooks, or we missed the
        # will_answer_card snapshot. Drop rather than emit a wrong event.
        _pending = None
        return

    queue = _pending["queue"]
    _seq += 1
    _events.append(
        {
            "seq": _seq,
            "kind": "answer",
            "ease": _pending["ease"],
            "wasNew": queue == QUEUE_TYPE_NEW,
            "wasLearning": queue in (QUEUE_TYPE_LRN, QUEUE_TYPE_DAY_LEARN_RELEARN),
            "wasReview": queue == QUEUE_TYPE_REV,
        }
    )
    log("addEvent: seq %s, ev %s" % (_seq, _events[-1]))
    _pending = None


def _on_state_did_undo(changes):
    global _seq
    if mw.state != "review":
        return
    if not changes.changes.card:
        return
    _seq += 1
    _events.append({"seq": _seq, "kind": "undo"})
    log("addEvent: seq %s, ev %s" % (_seq, _events[-1]))


gui_hooks.reviewer_will_answer_card.append(_on_will_answer_card)
gui_hooks.reviewer_did_answer_card.append(_on_did_answer_card)
gui_hooks.state_did_undo.append(_on_state_did_undo)


@JSCallable
def getNewAnswerEvents(sinceSeq):
    return [e for e in _events if e["seq"] > sinceSeq]
