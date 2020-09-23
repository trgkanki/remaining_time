# Changelog of remaining_time

In case you're using this addon well, consider supporting me via patreon!
If you encounter any bugs, submit through [Github issues](https://github.com/trgkanki/remaining_time/issues) page.

[![github](https://cdn.jsdelivr.net/gh/trgkanki/trgkanki-template-cli@develop/res/github_small.png)](https://github.com/trgkanki/remaining_time/issues)
[![patreon](https://cdn.jsdelivr.net/gh/trgkanki/trgkanki-template-cli@develop/res/patreon_small.png)](https://www.patreon.com/trgk)


[comment]: # (DO NOT MODIFY. new changelog goes here)

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
