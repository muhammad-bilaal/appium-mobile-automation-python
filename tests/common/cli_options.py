import pytest


def pytest_addoption(parser) -> None:
    """Register shared command-line options for mobile and web runs."""
    group = parser.getgroup("runtime config")
    group.addoption(
        "--platform",
        action="store",
        default="android",
        help="Target platform: android, ios, or web",
    )
    group.addoption(
        "--env",
        action="store",
        default="local",  # options: browserstack or local
        help="Execution environment: browserstack or local",
    )


@pytest.fixture(scope="session")
def platform(request):
    return request.config.getoption("--platform")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")
