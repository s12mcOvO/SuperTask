"""Local development entrypoint for SuperTask."""

from supertask.app import SuperTaskApp, SuperTaskAppMain, run_app

__all__ = ["SuperTaskApp", "SuperTaskAppMain", "run_app"]


if __name__ == "__main__":
    run_app()
