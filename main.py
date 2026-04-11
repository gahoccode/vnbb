"""CLI entrypoint for the vnbb terminal chart viewer."""

from app.bootstrap import build_application


def main() -> None:
    """Run the interactive stock chart application."""
    app = build_application()
    app.run()


if __name__ == "__main__":
    main()
