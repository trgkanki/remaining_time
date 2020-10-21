# Remaining Time 2.1 - Configuration

## debug (default: false)
Enable debug mode.

## showAtBottom (default: false)

When this is true, the progress bar will show at the bottom.

## runOnMobile (default: false)

Set plugin to run also on mobile. *Note) only compatible w/ AnkiDroid.*

## messageFormat (default: `"Elapsed %(elapsedTime),  Remaining %(remainingTime), ETA %(ETA)"`)

Format the messages. `%(variableName)` gets replaced to values below

- `%(elapsedTime)`: Elapse time since the start of the reviews.
- `%(remainingTime)`: Estimated remaining time.
- `%(totalTime)`: `elapsedTime + remainingTime`
- `%(CPM)`: Cards per minute.
- `%(ETA)`: Estimated time arrival. Expected review finish time
- `%(ETA12)`: Same as `ETA`, except that it's in 12-hour format (ex: `12:00 PM`)
- `%(RR)`: Retention rate for reviewed cards only. (ex: `80.0%`)
