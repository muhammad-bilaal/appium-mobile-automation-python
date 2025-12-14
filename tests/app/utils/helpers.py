from pathlib import Path

from tests.app.utils.constants import PACKAGE, UPDATED_APK_FILE, UPDATED_IPA_FILE


class Helpers:
    @staticmethod
    def get_apk_path(filename: str) -> str:
        current_file = Path(__file__).resolve()
        root_dir = current_file.parents[2]
        apk_path = root_dir / "app" / "apps" / filename
        return str(apk_path)

    @staticmethod
    def get_asset_path(filename: str) -> str:
        current_file = Path(__file__).resolve()
        root_dir = current_file.parents[2]
        apk_path = root_dir / "app" / "assets" / filename
        return str(apk_path)

    @staticmethod
    def update_app(driver, platform):
        if driver.is_app_installed(PACKAGE):
            driver.remove_app(PACKAGE)
        if platform == "android":
            new_apk_path = Helpers.get_apk_path(UPDATED_APK_FILE)
            driver.install_app(new_apk_path)
        else:
            new_ipa_path = Helpers.get_apk_path(UPDATED_IPA_FILE)
            driver.install_app(new_ipa_path, replace=True)

        driver.activate_app(PACKAGE)
