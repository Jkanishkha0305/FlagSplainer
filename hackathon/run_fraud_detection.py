"""
Convenience entry point for the fraud detection workflow.
"""

from .fraud_detection.runner import run_fraud_detection


def main() -> None:
    """Run the fraud detection pipeline."""
    run_fraud_detection()


if __name__ == "__main__":
    main()
