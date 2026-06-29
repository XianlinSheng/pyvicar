from collections.abc import Iterable


def assert_label(obj, name, label_type, iterable=False, recursive=False):
    if iterable and isinstance(obj, Iterable) and not isinstance(obj, str):
        for i, obj1 in enumerate(obj):
            assert_label(
                obj1,
                f"{name}[{i}]",
                label_type,
                iterable=iterable and recursive,
                recursive=recursive,
            )
    else:
        if not isinstance(obj, label_type):
            raise TypeError(
                f"Use Label {label_type} to create argument, got type {type(obj)} '{obj}' for argument {name}"
            )
