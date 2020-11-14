from ..utils.JSCallable import JSCallable
from aqt import mw


@JSCallable
def isQuestionSide():
    reviewer = mw.reviewer
    return reviewer.state == "question"
