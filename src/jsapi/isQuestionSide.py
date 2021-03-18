from ..utils.JSCallable import JSCallable
from aqt import mw


@JSCallable
def isQuestionSide():
    return mw.state == "review" and mw.reviewer.state == "question"


@JSCallable
def isOverview():
    return mw.state == "overview"
