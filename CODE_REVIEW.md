# GP_Calibration.py — Code Review

**Reviewed:** 2026-08-28 · **File:** `GP_Calibration.py` (439 lines) · **Method:** full read-through plus reproduction of each suspected failure against a scratch copy with stub state files.

Findings are ranked by operational consequence. Items 1–5 are confirmed crashes or silent data corruption; 6–10 produce wrong numbers without crashing.

---

## Confirmed crashes and corruption

### 1. `ZeroDivisionError` — a required course width of 0 kills the app (`:281`)

Init at `:317` accepts any float for required course width, with no positivity check — unlike PSB (`:334`) and both clearances, which reject `<= 0`. Entering `0`, then choosing menu option 2:

```
ZeroDivisionError: float division by zero
  File "GP_Calibration.py", line 281, in modifyPsb
    ...{round(transmitter.current_Psb + 20 * math.log10(course_width_FIU / transmitter.required_course_width),3)}...
```

A **negative** required course width fails the same line with `ValueError: math domain error`.

Two things combine here: the guard at `:275` (`math.log10(course_width_FIU)`) validates the value the operator just typed but never the stored `required_course_width`; and the failing expression sits inside the log-write line **after** the `try` block, so the surrounding `except ValueError` cannot catch it.

**Fix:** require `required_course_width > 0` at init, and validate it again before use in `modifyPsb`.

### 2. `KeyError: 'transmitter2'` on a partial state file (`:368`)

`loadStateFromFile` returns whatever it parsed, including a dict holding only `transmitter1`. The guard at `:300` (`if restore == 'n' or not transmitters:`) only tests for *empty*, so a one-transmitter dict skips initialization and reaches:

```
Restored successfully!
Traceback (most recent call last):
  File "GP_Calibration.py", line 368, in <module>
    tx2 = transmitters["transmitter2"]
KeyError: 'transmitter2'
```

Reproduced with a `data` file containing a single complete `transmitter1` block. Note the misleading "Restored successfully!" immediately before the traceback.

**Fix:** treat a load as successful only when both `transmitter1` and `transmitter2` are present; otherwise report the file as unusable and fall through to initialization.

### 3. `saveStateToFile` truncates the state file before writing (`:42`)

`open(datafile, "w")` empties the file the moment it opens, and this runs after *every* value change in all five modify routines. Any interruption inside that window — Ctrl+C, power loss, or the crashes in items 1 and 2 — leaves a truncated file, which is precisely the input that triggers item 2, or a parse failure that forces the operator to re-enter both transmitters from scratch.

**Fix:** write to `data.tmp`, then `os.replace(tmp, datafile)` — atomic on Windows and POSIX. Optionally keep the previous file as `data.bak`.

For a calibration record this is the highest-consequence item in the review: it is the one that can destroy data the operator cannot reconstruct.

### 4. `nan` and `inf` pass every validation gate and get persisted

`float("nan")` does not raise `ValueError`, and `math.log10(nan)` returns `nan` instead of raising — so the log10 guards at `:145` and `:275` do not catch it. `inf` likewise satisfies `if psb <= 0` and every other check.

Confirmed: entering `nan` for CL_DDM and `inf` for PSB at init produced a state file containing

```
CLDDM: nan
current_Psb: inf
```

with the app continuing to run and reporting `NEW DDM IS nanμA (nan%)`. The values reload cleanly on the next run, so the corruption persists silently across sessions.

**Fix:** add `math.isfinite(value)` to every numeric parse — the init prompts and all five modify routines.

### 5. `UnicodeEncodeError` when stdout is redirected

The menu, the tables, and several prompts contain `μ` (U+03BC). Interactive use is fine because Python writes the Windows console through the wide-character API, but redirecting to a file:

```
python GP_Calibration.py > session.txt
'charmap' codec can't encode character 'μ' ... : character maps to <undefined>
```

Any attempt to capture a calibration session to a transcript fails partway through, after some values may already have been changed and saved.

**Fix:** `sys.stdout.reconfigure(encoding="utf-8")` at startup (and open `logfile` with `encoding="utf-8"` for consistency, though its contents are currently ASCII).

### Also unhandled

`EOFError` and `KeyboardInterrupt` at any prompt produce a raw traceback, as does any `OSError` from the log or state writes (file locked by another program, disk full). State is saved after each individual edit, so a mid-session abort loses at most the current entry — but the operator sees a stack trace rather than a message.

---

## Wrong values, no crash

### 6. `width_narrow` / `width_wide` go stale after a PSB change (`:263`–`:286`)

Both are derived from `current_Psb ± 20·log10(1.18)` in the constructor (`:12`, `:13`) and recomputed only inside `changeCourseWidth`. `modifyPsb` updates `current_Psb` and leaves them untouched. Observed:

| Menu row | Before | After `modifyPsb` |
|---|---|---|
| `2. Tx1 psb` | 20.0 dbm | **22.499 dbm** |
| `5. Tx1 width_narrow` | 21.438 dbm | 21.438 dbm *(unchanged — still 20 ± 1.438)* |
| `6. Tx1 width_wide` | 18.562 dbm | 18.562 dbm *(unchanged)* |

The menu displays, and the state file stores, 18% points belonging to the *previous* PSB. Operationally this is the most concerning non-crash finding, because the stale numbers are presented with the same authority as the live ones.

**Fix:** depends on intent — see open question 1.

### 7. `modifyClddm90` reports the percentage of the wrong parameter (`:222`)

```python
print(f"NEW CL_DDM_90 IS {transmitter.clddm_90}μA ({round(transmitter.current_DDM * 0.1033, 3)}%) \n")
```

The percentage converts `current_DDM`, an unrelated parameter, rather than the CL_DDM_90 value just entered. `modifyClddm150` at `:239` uses its own value, confirming this as a copy-paste slip. The operator sees a correct μA figure beside a percentage that does not belong to it.

### 8. `changeCourseWidth` logs the wrong current value in the wide branch (`:154`)

```python
f.write(f"... Course width wide PSB is {round(transmitter.width_narrow,3)}, ...")
```

The `negative` (wide) branch reports `width_narrow`. Since the log file *is* the calibration record, every wide-side adjustment is recorded against the narrow value.

### 9. `constraints` is computed and never read (`:21`, `:25`, `:29`)

Every `Transmitter` gets a per-category `[12, 20]` / `[10, 15]` / `[5, 12]`, referenced nowhere else in the file. Either unfinished range validation or dead weight — worth resolving, because nothing currently bounds entered values against category limits.

### 10. Relative paths resolve against the working directory (`:4`, `:5`)

`logfile = "log.txt"` and `datafile = "data"` are relative. Launching from a different working directory — a desktop shortcut, a scheduled task, a different shell — silently reads a *different* state file and reports "Data file not found", inviting re-initialization while the real state sits elsewhere.

**Fix:** anchor both to the script's own directory via `pathlib.Path(__file__).parent`.

---

## Minor

- `printTable` prints the literal string `"/n"` — forward slash, not an escape (`:186`).
- `modifyClddm`'s log line reads `value is{25.0}`, missing a space (`:259`).
- `changeCourseWidth` prompts for "between 5 to 20" but accepts any positive number; `500` is taken without complaint (`:139`).
- A non-numeric entry in `changeCourseWidth` reports "Value should be non-negative", which misdescribes the actual problem — one `except ValueError` covers both the parse failure and the log10 domain error (`:147`).
- `restore` matches only exactly `y`; typing `yes` routes silently into full re-initialization, which overwrites the saved state at `:363` (`:290`).
- `logState` runs only on fresh initialization, so a restored session's starting values never enter the log (`:362`).
- `case _: print("Invalid choice")` in the main loop is unreachable — the range is validated before the `match` (`:433`).

---

## Open questions before fixing

1. **Should `width_narrow` / `width_wide` track PSB?** Recompute them in `modifyPsb` (overwriting any manual adjustment from menu 5/6), keep them independent as today, or recompute only while they are still constructor-derived?
2. **Should PSB be allowed ≤ 0 after edits?** Init rejects `psb <= 0`, but `modifyPsb` produced `-5.021 dbm` in testing. Which rule is correct?
3. **What was `constraints` meant to enforce?** If it is intended range validation, on which parameter?

---

## What was tested

Each crash was reproduced by running a copy of the script in a scratch directory with stub state files, driving it via piped stdin under `PYTHONIOENCODING=utf-8`:

| # | Input | Result |
|---|---|---|
| 1 | required course width `0`, then menu 2 | `ZeroDivisionError` at `:281` |
| 1 | required course width `-3`, then menu 2 | `ValueError: math domain error` at `:281` |
| 2 | `data` file with only a `transmitter1` block | `KeyError: 'transmitter2'` at `:368` |
| 4 | `nan` for CL_DDM, `inf` for PSB at init | accepted, persisted, `NEW DDM IS nanμA (nan%)` |
| 5 | stdout redirected to a file | `UnicodeEncodeError` on the first `μ` |
| 6 | menu 2 changing PSB 20.0 → 22.499 | rows 5 and 6 unchanged at 21.438 / 18.562 |

Not covered: concurrent access to `data` by two instances, and behaviour on a read-only or full disk.
