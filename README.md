# healthops

Runs the health plan, Todo Plan and daily log on your own machine. One Python
file, no packages to install, and your log stays on your disk.

## Run it

Needs Python 3.8 or newer (already on macOS and most Linux; on Windows install it from python.org).

```bash
git clone https://github.com/ramasdf-ai/healthops
cd healthops
python3 server.py
```

Open http://localhost:8000. It lands on the daily log. Stop the server with Ctrl+C.

Options:

```bash
python3 server.py --port 9000        # different port
python3 server.py --host 0.0.0.0     # log from your phone on home Wi-Fi
```

With `--host 0.0.0.0`, open `http://<your-computer's-IP>:8000` on your phone.
There is no login, so only do this on a network you trust.

## Pages

| Page | What it is |
| --- | --- |
| `/log.html` | Rotation Daily Log: today's promise with kept/not-kept tally and streak, Oura readiness call, evening check-in, 7-day averages |
| `/todo.html` | Todo Plan: morning promise, daily steadiness routine, weekly review |
| `/plan.html` | Rotation Strength Plan: training queue, readiness rules, labs, nutrition |
| `/focus.html` | Focus and Steadiness Plan: evaluation prep and questions |

## Your data

Log entries save as you type to `data/days.json`, one entry per date. The
`data/` folder is in `.gitignore`, so your health log is never committed.
Back it up by copying that file.

## How it works

- `server.py` serves `public/` and two endpoints: `GET /api/days` returns all
  entries, `PUT /api/days/YYYY-MM-DD` saves one. Writes go to a temp file
  and then replace `days.json`, so a crash can't corrupt it.
- `public/local-db.js` connects the log page to those endpoints, so the
  page itself is unchanged from the claude.ai version.
- The plan pages are static copies of the claude.ai pages (as of 4 Nov 2026),
  with links pointing to each other.
