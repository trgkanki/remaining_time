# Changelog of remaining_time

In case you're using this addon well, consider supporting me via [patreon](https://www.patreon.com/trgk)!
If you encounter any bugs, submit through [Github issues](https://github.com/trgkanki/remaining_time/issues) page.

[![github](https://cdn.jsdelivr.net/gh/trgkanki/trgkanki-template-cli@develop/res/github_small.png)](https://github.com/trgkanki/remaining_time/issues)
[![patreon](https://cdn.jsdelivr.net/gh/trgkanki/trgkanki-template-cli@develop/res/patreon_small.png)](https://www.patreon.com/trgk)

<details>
  <summary>🎉 Special thanks to ...</summary>
  
  ## Patreons
  - abed
  - Sven

  # Developers
  - [Glutaminate](https://github.com/glutanimate/)
  - [Dae](github.com/dae/)

</details>

---------

[comment]: # (DO NOT MODIFY. new changelog goes here)

## 24.1.22i135 (2024-01-22)

- 23.10+ fix 2

## 24.1.22i134 (2024-01-22)

- basic 23.10 support
- fix reset progress bar hotkey
- js now overview compatible

## 20.12.13i151 (2020-12-13)

If you like the ongoing support of this addon consider buying me a cup of coffee via [patreon](https://www.patreon.com/trgk)!

- Fix: frequent resetting of entire progress bar. For better usability addon will NEVER reset the progress bar on any instance. You should manually reset them as seem appropriate.
- Fix: mobile support for long learning session. Progress bar will update faithfully.
- Fix: FOUC on AnkiDroid
- Feature: (experimental) added fixed-width segment mode. IDK why, but it is requested.

## 20.11.20i48 (2020-11-20)

- fix: dark mode (again)
- fix: undo undoes the progress bar, edit card now don't touch the progress bar (most of the time)

## 20.11.15i135 (2020-11-15)

- Hotfix: 'again' recorded as 'good' ([Issue #24](https://github.com/trgkanki/remaining_time/issues/26))
- Fix: possible bar blinkering on AnkiDroid

## 20.11.12i113 (2020-11-12)

- Feature: you can add custom css to the progress bar (#15)
- Fix: message: no line break, better align to center
- Fix: code fix for model update. Better compatibility for Anki 2.1.25+

## 20.10.21i160 (2020-10-22)

- Fix: showAtBottom now works on mobile
- Feature: `%(RR)` for retention rate format
- Debug: added support for debug log (see menu `Help > Show addon log: Remaining Time`)

## 20.9.25i145 (2020-09-25)

Fix issues with AnkiDroid support.

## 20.9.22i38 (2020-09-22)

- Fixes `main.min.map` related inspector error
- Fixes card CSS interfering w/ progress bar styling
- Progress bar message now customizable on addon config.

## 20.9.12i225 (2020-09-13)

- Fixes confirm message so that user can 
- Re-fixes compatibility w/ [Hint Hotkeys](https://ankiweb.net/shared/info/1844908621) addon.

## 20.8.25i52 (2020-08-25)

Hotfix: compatibility w/ Anki 2.1.30+. Fixes this error

```
File "anki/hooks.py", line 635, in repl
TypeError: new_body_class() got multiple values for argument '_old' 
```

## 20.8.24i181 (2020-08-25)

- Rewritten everything in typescript
  - This may be a major breaking change!
- Compatible w/ AnkiDroid
- Better support for night mode
