# Remaining Time 2.1 - Configuration

## debug (default: false)
Enable debug mode.

## showAtBottom (default: false)

When this is true, the progress bar will show at the bottom.

## runOnMobile (default: false)

Set plugin to run also on mobile. *Note) only compatible w/ AnkiDroid.*

## fixedSegmentWidth (default: false)

Set all segment's width to same. [This has been requested](https://github.com/trgkanki/remaining_time/issues/25), so FYI.

## messageFormat (default: `"Elapsed %(elapsedTime),  Remaining %(remainingTime), ETA %(ETA)"`)

Format the messages. `%(variableName)` gets replaced to values below

- `%(elapsedTime)`: Elapse time since the start of the reviews.
- `%(remainingTime)`: Estimated remaining time.
- `%(totalTime)`: `elapsedTime + remainingTime`
- `%(CPM)`: Cards per minute.
- `%(ETA)`: Estimated time arrival. Expected review finish time
- `%(ETA12)`: Same as `ETA`, except that it's in 12-hour format (ex: `12:00 PM`)
- `%(RR)`: Retention rate for reviewed cards only. (ex: `80.0%`)

## barCSS (Default: `""`) - *Experimental*

CSS stylesheet that only gets applied inside the progress bar. What selector to use is intentionally undocumented, so that we could change our implementation details as much as we want. Be careful as your code *may* break every time the addon is updated.

To see what selectors to use, try using [AnkiWebView Inspector](https://ankiweb.net/shared/info/31746032) addon.
