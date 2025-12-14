# Automation Test

## Document Structure
```
automation-test/
├── src/                                    # Source code for the application
│   ├── user.py                             # Handles user-related logic (e.g., authentication, profiles)
│   ├── order.py                            # Manages order-related functionality (e.g., creation, updates)
│   └── api/                                # API-related source code (e.g., endpoints, services)
├── tests/                                  # Test code for the project
│   ├── common/                             # Shared modules or utilities for tests
│   ├── unit/                               # Unit tests for individual components
│   │   ├── test_user.py                    # Unit tests for user-related functionality
│   │   └── test_order.py                   # Unit tests for order-related functionality
│   ├── api/                                # API tests for endpoints and services
│   │   └── test_api.py                     # Test cases for API functionality
│   ├── web/                                # Web UI tests using automation tools (e.g., Selenium)
│   │   ├── pages/                          # Page Object models for web pages
│   │   │   ├── login_page.py               # Page Object for login page
│   │   │   └── dashboard_page.py           # Page Object for dashboard page
│   │   └── test_web.py                     # Test cases for web UI functionality
│   ├── app/                                # Mobile app tests using automation tools (Appium)
│   │   ├── apps/                           # App and APK files
│   │   │   ├── ios_app.app                 # Place iOS simulator build here
│   │   │   └── android.apk                 # Place Android emulator build here
│   │   ├── configs/                        # Desired capabilities for Appium
│   │   │   ├── android_caps.json           # Android capabilities
│   │   │   └── ios_caps.json               # iOS capabilities
│   │   ├── drivers/                        # Appium & Sauce Lab Drivers
│   │   │   ├── driver_factory.py           # Driver loader for Appium
│   │   │   └── sauce_lab_driver.py         # SauceLab Driver
│   │   ├── pages/                          # Page Object models for mobile app screens
│   │   │   ├── login_screen.py             # Page Object for mobile login screen
│   │   │   └── payment_screen.py           # Page Object for mobile payment screen
│   │   ├── utils/                          # Helpers and utilities for mobile app tests
│   │   │   ├── locators.py                 # Locators for mobile app screens
│   │   │   ├── look_up.py                  # Look up utilities for mobile app screens
│   │   │   └── timers.py                   # Time out utilities for mobile app screens
│   │   ├── tests/                          # Test files for mobile app functionality
│   │   │   └── test_dashboard_loading.py   # Mobile test cases
│   │   ├── pytest.ini                      # Configuration file for Pytest settings
│   │   ├── conftest.py                     # Pytest fixture configuration for app
│   │   └── README.md                       # Readme for mobile app tests
│   ├── integration/                        # Integration tests for system-wide functionality
│   │   └── test_db.py                      # Tests for database interactions
│   ├── data/                               # Test data files for various test cases
│   │   └── users.json                      # JSON file containing user data for tests
│   └── conftest.py                         # Global Pytest fixture configuration
├── reports/                                # Directory for test reports and outputs
│   ├── allure-results/                     # Allure test report results
│   ├── htmlcov/                            # Code coverage reports in HTML format
│   └── screenshots/                        # Screenshots for failed web and app tests
├── requirements.txt                        # Project dependencies for Python packages
├── pytest.ini                              # Configuration file for Pytest settings
└── .gitignore                              # Git ignore file for excluding files from version control
```
## How to run test cases locally
### clone codes
```
git clone https://gitlab.gettr.fyi/alex1/automation-test.git
```
### Install Pyhon and create a virtual env
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### run pytest
`Note:` This will run all the test cases excluding the mobile app tests
```commandline
pytest
```

### Run mobile app tests
To run the mobile app test cases refer to [Mobile App Automation Testing with Appium & Pytest](tests/app/README.md)

#### Quick Commands for Mobile Testing

**Local Testing:**
```bash
# Run all Android tests locally
pytest --platform=android --env=local tests/app/tests

# Run specific home page explore test locally
pytest --platform=android --env=local tests/app/tests/smoke_tests/home_page/test_explore_tab_post_interactions_and_scrolling.py -v -s
```

**BrowserStack Cloud Testing (via SDK):**
```bash
# Run Android home page explore test on BrowserStack
browserstack-sdk pytest --platform=android --env=browserstack tests/app/tests/smoke_tests/home_page/test_explore_tab_post_interactions_and_scrolling.py -v -s
```

**Prerequisites for BrowserStack:**
- Populate `browserstack.yml` (or export overrides such as `BROWSERSTACK_USERNAME`, `BROWSERSTACK_ACCESS_KEY`, `BROWSERSTACK_ANDROID_APP_ID`, `BROWSERSTACK_IOS_APP_ID`)
- Set authentication variables: `USERNAME`, `PASSWORD`
## Generate Test Reports

## Code Quality Automation
- Install the Git hook tooling with `pre-commit install` after setting up your virtualenv. This runs `ruff` (lint + format) and common sanity checks before every commit.
- You can manually run the same checks via `pre-commit run --all-files`.
- The `quality_checks` GitLab job (see below) executes `pre-commit` and a lightweight `pytest` run on every merge request update so contributors cannot skip the local hooks.
- Run `scripts/install-hooks.sh` once to point Git at the enforced hooks in `.githooks/`; any commit attempted without `pre-commit` available now fails immediately.

## CI/CD Pipeline

Automated GitLab pipeline that runs repository quality checks and a scheduled dependency updater.

### How to Trigger

**Manual Trigger (Recommended):**
1. Navigate to GitLab project → **Build > Pipelines**
2. Click **Run Pipeline** → Select branch → **Run Pipeline**

**Individual Jobs:**
- Trigger `quality_checks` or `monthly_dependency_update` manually if needed.

### Pipeline Stages

1. **Quality**: Runs `pre-commit` (ruff lint + format) and `pytest -m "not stage_1" --maxfail=1` on every merge request and default-branch push. The job adds a status comment to the MR for quick visibility.
2. **Maintenance**: Scheduled `monthly_dependency_update` job refreshes `requirements.txt`, pushes a branch, and optionally opens a merge request when a `GITLAB_TOKEN` with `api` scope is present.

### Additional Pipeline Configuration

- Define `GITLAB_TOKEN` (personal access token with `api` scope) to let the monthly dependency job open merge requests automatically. Without it, the job only pushes the update branch.
- Optionally override `BOT_EMAIL` and `BOT_NAME` CI variables to customize the commit identity used by the dependency updater.

### Results & Troubleshooting

**View Results:**
- GitLab job logs and artifacts (e.g., `precommit.log`).
- Merge request comments from the quality job.

**Common Issues:**
- Missing `GITLAB_TOKEN` prevents automatic MR creation from the dependency update job.
- Run `scripts/install-hooks.sh` locally so commits align with the enforced pre-commit hook.
