class ReplaceBlock:
    def __init__(self, startMarker, endMarker, script):
        self.startMarker = startMarker
        self.endMarker = endMarker
        self.script = script
        self.blockRaw = "%s%s%s" % (startMarker, self.script, endMarker)

    def included(self, targetString):
        return self.blockRaw in targetString

    def apply(self, targetString, *, updated=None):
        oldTargetString = targetString
        targetString = removeReplaceBlock(
            targetString, self.startMarker, self.endMarker
        )
        targetString = self.blockRaw + "\n\n" + targetString

        if updated and oldTargetString != targetString:
            updated[0] = True

        return targetString


def removeReplaceBlock(targetString, startMarker, endMarker, *, updated=None):
    oldTargetString = targetString
    while True:
        try:
            start = targetString.index(startMarker)
            end = targetString.index(endMarker, start + 1)
            targetString = (
                targetString[:start] + targetString[end + len(endMarker) :]
            ).strip()
        except ValueError:
            break

    if updated and oldTargetString != targetString:
        updated[0] = True

    return targetString
