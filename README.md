# DevOps Interview Lab

DevOps Interview Lab is a practical interview question bank and training application for junior IT, DevOps, Cloud, and Infrastructure candidates.

## Who it's for

- Junior IT, DevOps, Cloud, and Infrastructure candidates preparing for interviews.
- Teams and mentors looking for a structured, hands-on way to practice common interview topics.

## Current status

This project is in early development. A minimal Flask web MVP is the product-facing layer today; no data store or deployment model has been selected yet. The question bank, the initial role and company profiles, a reusable interview builder, the web MVP, and a temporary CLI practice session are available. The CLI is a development and testing interface for the reusable core, not the product. The core has no external dependencies; Flask is the only external dependency and is used by the web layer only.

## Installation

Python 3.12 is used in CI. From the repository root, create an isolated virtual environment and install the declared dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Flask is pinned in `requirements.txt` and the Python 3.12 test suite runs in GitHub Actions. The web server uses Flask's development server with debugging disabled and binds to `127.0.0.1`; it is intended **only for local practice**, not public deployment. Session cookies are HttpOnly and SameSite=Lax, with Secure disabled for local HTTP. A new random signing key is generated at each application startup, so interview state stored in the signed browser cookie is invalidated on server restart. Form requests are limited to 16 KiB. There is no CSRF token mechanism, authentication, persistent storage, or deployment hardening; these must be reviewed before any public deployment.

## Usage

Run the web MVP from the repository root, then open http://127.0.0.1:5000:

```bash
python -m src.web
```

On the home page, choose a role (required), an optional company, a difficulty and a question count, then start the interview. You then work through the questions one at a time: write your answer in the textarea, reveal the reference answer on request, and move to the next question. After the last question you reach a completion screen where you can start a new interview. The interview lives only in your browser session; nothing is stored on a server.

Run the temporary CLI practice session instead:

```bash
python -m src.cli.main
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Automated checks

GitHub Actions runs the Python `unittest` suite and a blocking `pip-audit` dependency vulnerability scan on pushes to `main` and on pull requests. You can run the test suite locally with the command above. Passing these checks does not establish production security.

## Planned areas

The project will cover practical questions and training across the following areas:
- Linux
- Networking
- Azure
- Git
- CI/CD
- Docker
- Kubernetes
- Security
- Windows Server
- Active Directory / Entra ID
- Scripting
- Troubleshooting

## Development approach

We build incrementally with a focus on simplicity: keep the project small and understandable, avoid overengineering, and ensure every file has a clear purpose. Production readiness will be added gradually.

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.
