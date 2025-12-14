# Mobile App Automation Testing with Appium & Pytest

This project is a mobile automation framework built with:

Appium

Python + Pytest

Optional BrowserStack support

Screenshots on failure

Rich logging per test run

HTML + Allure reports

### Project Structure

```
 conftest.py                   # Global fixtures, logger, Sauce config
 requirements.txt              # All dependencies
 tests/
     app/
         apps/                 # app and apk
         configs/              # Desired capabilites for iOS and Android
         drivers/              # Appium & BrowserStack Drivers
         pages/                # Page objects
         tests/                # Test files
         utils/                # Helpers (e.g., assertions)
         pytest.ini            # configuration for pytest
         conftest.py           # Pytest fixture configuration for app
         README.md             # Readme
 reports/
    logs/                     # Logs per run
    screenshots/             # Screenshots on failure
```

`Note:` If this is first time running this project, follow iOS and Android setup instructions.

#### [ Android Setup](./README_ANDROID.md)

#### [ iOS Setup](./README_IOS.md)

### Setup

#### 1. Install Python dependencies

```
pip install -r requirements.txt
```

#### 2. (Optional) Set environment variables for BrowserStack

```
export BROWSERSTACK_USERNAME=your-username
export BROWSERSTACK_ACCESS_KEY=your-access-key
```

### Running the Tests

Run tests locally on Android:

```
pytest --platform=android --env=local tests/app/tests
```

Run tests on BrowserStack:

```
pytest --env=browserstack --platform=android tests/app/tests
```

Run tests locally on iOS:

```
pytest --platform=ios --env=local tests/app/tests
```

Run tests on BrowserStack:

```
pytest --env=browserstack --platform=ios tests/app/tests
```

Run BrowserStack cloud tests with the SDK:

```
browserstack-sdk pytest --platform=android --env=browserstack tests/app/tests
```

The SDK reads configuration from `browserstack.yml` and streams rich context (observability, logs, videos) to the BrowserStack dashboard automatically.
Override credentials or app ids by exporting `BROWSERSTACK_USERNAME`, `BROWSERSTACK_ACCESS_KEY`, `BROWSERSTACK_ANDROID_APP_ID`, and `BROWSERSTACK_IOS_APP_ID` (see `browserstack.yml` for details).

Run BrowserStack tests with dynamic app fetching:

```
APP_VERSION=1.74.5 pytest --platform=android --env=browserstack tests/app/tests
```

When `APP_VERSION` is set, the framework will automatically fetch the latest app build matching that version from BrowserStack APIs. The platform is determined from the `--platform` parameter.

Run a specific test:

```
pytest --platform=android --env=local tests/app/tests/test_dashboard_loading.py
```

#### Test Reports

Automatically created if pytest-html is installed. The report will be saved in the `reports` directory.
Find the report in `reports/test_report.html`.
Video & screenshots can be found in the `reports/videos` and `reports/screenshots` directories.
Video is only retained for the failed test cases on local environment.

#### HTML Report

```
open reports/test_report.html
```

#### Allure Report

2.  Ensure You’re Generating Allure Results, and allure is installed on your system

```
allure generate reports/allure-results -o reports/allure-report --clean
```

Or if you want to open it directly:

```
allure serve reports/allure-results
```
