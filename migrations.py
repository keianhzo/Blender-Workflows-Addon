import bpy


def migrate():
    for version in MIGRATIONS:
        for step in MIGRATIONS[version]:
            step(version)


MIGRATIONS = {
}
