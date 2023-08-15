import os
import re


def parse_label_name(label_name):
    if result := re.search(r"^([+-])\[(.+)\s(.+)\]", label_name):
        symbol, class_name, method_name = result.groups()
        params_count = method_name.count(":")
        params = tuple("arg%d" % (i + 2) for i in range(params_count))
        method_name = method_name.replace(":", ":(id)%s ") % (params)
        method_name = "%s (%%s)%s" % (symbol, method_name)
        return (class_name, method_name)
    else:
        return (None, None)


def find_sub_function(pseudo_code: str) -> list[str]:
    """Find sub function names from pseudo code."""
    if m := re.findall(r"(sub_[a-zA-Z0-9]+)", pseudo_code):
        return list(set(list(m)))

    return []


def is_sub_function(label_name: str) -> bool:
    """Check if label name is sub function."""
    return bool(m := re.match(r"(sub_[a-zA-Z0-9]+)", label_name))


document = Document.getCurrentDocument()
segment = document.getSegmentByName("__TEXT")
print(f"Procedure count: {segment.getProcedureCount()}")

app_name = document.getExecutableFilePath().split("/")[-1]
print(f"App name: {app_name}")

MAXIMUM = 100
codes: str = ""
for i in range(segment.getProcedureCount()):
    procedure = segment.getProcedureAtIndex(i)
    address = procedure.getEntryPoint()
    label_name = segment.getNameAtAddress(address)
    pseudo_code = procedure.decompile()
    if not label_name or not pseudo_code:
        continue

    if is_sub_function(label_name):
        # TODO: How to find the number of arguments, their data types, and the return type?
        # TODO: How can I distinguish between a class method and an instance method?
        # int sub_100012a9c() {}
        # void sub_10005386c(int arg0, int arg1, int arg2) {}
        code: str = "%s\n{\n%s}\n\n" % (label_name, pseudo_code)
        codes += code

    if i % MAXIMUM == 0:
        print(f"i: {i}")
        path = os.path.expanduser(f"~/Decompile/{app_name} - {int(i/MAXIMUM)}.m")
        with open(path, "w", encoding="utf-8") as f:
            f.write(codes)

        codes = ""
