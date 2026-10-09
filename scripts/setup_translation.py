
import argostranslate.package

FROM_CODE = "nl"
TO_CODE = "en"

print("Fetching available translation packages...")
argostranslate.package.update_package_index()

packages = argostranslate.package.get_available_packages()
package = next(
    (
        p for p in packages
        if p.from_code == FROM_CODE and p.to_code == TO_CODE
    ),
    None,
)

if package is None:
    raise RuntimeError("Dutch-to-English package was not found.")

print("Downloading and installing Dutch-to-English model...")
download_path = package.download()
argostranslate.package.install_from_path(download_path)

print("Translation model installed successfully.")