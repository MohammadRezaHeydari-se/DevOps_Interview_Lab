# DevOps Interview Lab

DevOps Interview Lab is a practical interview question bank and training application for junior IT, DevOps, Cloud, and Infrastructure candidates.

## Who it's for

- Junior IT, DevOps, Cloud, and Infrastructure candidates preparing for interviews.
- Teams and mentors looking for a structured, hands-on way to practice common interview topics.

## Current status

This project is in early development. The target product is a web application; no web framework has been selected yet. The question bank, the initial role and company profiles, and a minimal CLI practice session are available today. The CLI is a temporary development and testing interface for the reusable core, not the product. Everything runs on the Python 3 standard library, with no external dependencies.

## Usage

Run a practice session from the repository root:

```bash
python3 -m src.cli.main
```

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

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
