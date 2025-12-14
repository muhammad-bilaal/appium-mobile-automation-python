# Mobile Automation Framework (Appium + Python)

## 📌 Overview

This repository demonstrates a **production-grade mobile automation framework** built with **Python, Pytest, and Appium**, designed for **real-world Android and iOS testing**.

The framework supports **local and cloud-based execution (BrowserStack)** and follows **enterprise-level automation practices** including driver factories, platform separation, CI/CD integration, and strict code quality enforcement.

## 🎯 Use Cases

- End-to-end mobile regression testing
- Cross-platform Android & iOS automation
- Cloud device testing with BrowserStack
- CI-driven mobile test execution
- Scalable automation for growing test suites

> ⚠️ **Important Note**: Mobile app binaries (`.apk`, `.ipa`, `.app`) are **NOT stored in this repository** due to GitHub size limits. Please follow the instructions below to configure them locally or via cloud providers.

---

## 📂 Project Structure

```
tests/
├── api/              # API automation
├── app/              # Mobile automation (Appium)
│   ├── pages/        # Page Object Models
│   ├── drivers/      # Driver factories
│   ├── tests/        # Mobile test cases
│   ├── configs/      # Capabilities
│   └── utils/        # Utilities
```

---

## 🚀 Getting Started (Local Setup)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/muhammad-bilaal/appium-mobile-automation-python.git
cd appium-mobile-automation-python
```

### 2️⃣ Create Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Running Tests

### 🔹 Run All Tests (Except Mobile)

```bash
pytest
```

---

## 📱 Mobile App Testing (Appium)

> Mobile binaries are **not committed** to Git. You must provide them locally or via cloud services.

### 📌 Local Mobile Testing

```bash
# Run all Android tests locally
pytest --platform=android --env=local tests/app/tests

# Run a specific test
pytest --platform=android --env=local \
  tests/app/tests/smoke_tests/home_page/test_explore_tab_post_interactions_and_scrolling.py -v -s
```

### ☁️ BrowserStack Cloud Testing

```bash
browserstack-sdk pytest --platform=android --env=browserstack \
  tests/app/tests/smoke_tests/home_page/test_explore_tab_post_interactions_and_scrolling.py -v -s
```

#### 🔐 BrowserStack Prerequisites

* Configure `browserstack.yml` **OR** export environment variables:

  * `BROWSERSTACK_USERNAME`
  * `BROWSERSTACK_ACCESS_KEY`
  * `BROWSERSTACK_ANDROID_APP_ID`
  * `BROWSERSTACK_IOS_APP_ID`
* Set app credentials:

  * `USERNAME`
  * `PASSWORD`

---

## 📊 Test Reports

* **Allure Reports**: Generated in `reports/allure-results`
* **Coverage Reports**: Available in `reports/htmlcov`
* **Screenshots**: Saved automatically for failed tests

---

## ✅ Code Quality Automation

* Install pre-commit hooks:

```bash
pre-commit install
```

* Run checks manually:

```bash
pre-commit run --all-files
```

### Enforced Checks

* `ruff` (lint + format)
* Common sanity & security checks
* Lightweight pytest execution

> ⚠️ Commits without pre-commit validation will fail.

---

## 🔄 CI/CD Pipeline (GitHub Actions)

The framework includes a GitHub Actions pipeline to ensure:

- Code quality validation via pre-commit (ruff)
- Stable test execution using Pytest
- Pull request protection (blocks merge on failure)

### Triggers
- Every push
- Every pull request

### Secrets
- GITHUB_TOKEN (auto-provided by GitHub Actions)

### 🧠 Best Practices

1 - ❌ Do NOT commit .apk / .ipa / .app files

2 - ✅ Store mobile apps in cloud storage or CI providers (e.g., BrowserStack)

3 - ✅ Keep the repository lightweight and fast

4 - ✅ Follow Page Object Model (POM) strictly

5 - ✅ Separate Android and iOS logic clearly

### 👤 Maintainer

**Muhammad Bilaal**  
**Senior QA Automation Engineer | Mobile & Web**

Automation Engineer with **4–5 years of hands-on experience** in **mobile (Appium), web (Playwright, Cypress), and API automation**. Specialized in **scalable frameworks, cloud device testing, and CI/CD-driven quality pipelines**.

- GitHub: https://github.com/muhammad-bilaal  
- LinkedIn: https://linkedin.com/in/bilaal-rajput-17a465278

⭐ **Happy Testing 🚀**!
