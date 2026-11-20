"""Print the installed directory to use as an npm file dependency."""

from scitex_rich_pdf import get_frontend_package_dir

if __name__ == "__main__":
    print(get_frontend_package_dir())
