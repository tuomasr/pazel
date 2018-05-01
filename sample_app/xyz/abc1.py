from foo import sample  # Import from foo's public interface.
from foo import foo     # Import a module with the same name as the package.


def main():
    print(sample())


main()
