from anki import version
anki21 = version.startswith("2.1.")

if anki21:
  from . import cloze_hide_all_21
else:
  from . import cloze_hide_all_20

