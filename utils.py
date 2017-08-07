# Copyright (c) 2017 Ultimaker B.V.
# CuraSolidWorksPlugin is released under the terms of the LGPLv3 or higher.

import subprocess

##  If successful returns a list of all currently running processes, including
#   the following fields:
#   - caption: Caption of the process, usually looks like this: "<something>.exe"
#   - process_id: process ID
#   If unsuccessful, return None.
def getAllRunningProcesses():
    args = ["wmic", "/OUTPUT:STDOUT", "PROCESS", "get", "Caption,ProcessId"]
    p = subprocess.Popen(args, stdout=subprocess.PIPE)

    out, _ = p.communicate()
    out = out.decode('utf-8')

    # sanitize the newline characters
    out = out.replace("\r\n", "\n")
    out = out.replace("\r", "\n")
    while out.find("\n\n") != -1:
        out = out.replace("\n\n", "\n")

    lines = out.split("\n")
    if len(lines) < 2:
        return

    # the first line is header
    result_list = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        # get caption and process id
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            continue

        caption, process_id = parts
        caption = caption.strip()
        process_id = int(process_id)

        result_list.append({"caption": caption,
                            "process_id": process_id})
    return result_list
