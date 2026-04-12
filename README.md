# Swapping ebuilds

## Links

* https://github.com/turulomio/swapping_ebuilds/
* https://pypi.org/project/swapping_ebuilds/

## What is swapping_ebuilds?

It is a script designed to detect when compiling ebuilds in Gentoo Linux causes system swapping. With this tool, you can identify memory-hungry compilations on computers with limited RAM and optimize their compilation times.

Once you detect swapping ebuilds, you can change this behavior by using `/etc/portage/package.env` to reduce the number of parallel processes during compilation, which lowers the required RAM.

For example, if your `MAKEOPTS` in `/etc/portage/make.conf` uses `-j4`, and `dev-qt/qtwebengine` compilation is swapping, you can force it to use only `-j2` for this particular ebuild. First, create a file at `/etc/portage/env/makeopts-j2`:

```bash
MAKEOPTS="-j2"
```

and then edit `/etc/portage/package.env`
```
dev-qt/qtwebengine makeopts-j2
```

The next time you compile `dev-qt/qtwebengine`, Gentoo will use only 2 concurrent processes.

## Usage

Main Actions (Mutually Exclusive - you must choose one):

Optional Parameters (can be used with the main actions):

The script supports the following main actions. You must choose one:

*   **`--get`**: Generates the log. When run with this argument, the script continuously monitors your system's swap usage and identifies the currently active ebuild (Gentoo package compilation). If it detects a change in swap usage while an ebuild is compiling, it logs this information to `/var/lib/swapping_ebuilds.txt`. This action is typically run in the background.
*   **`--analyze`**: Analyzes the log. After collecting data with `--get`, use this to read the log file and generate a summary report. This report shows which ebuilds caused significant swapping, their average swap usage, and how long they were active.
*   **`--list`**: Lists raw log entries. Prints each individual entry recorded in the log file in chronological order.
*   **`--clean`**: Cleans the log. Deletes the log file (`/var/lib/swapping_ebuilds.txt`), effectively clearing all previously recorded swap data.

### Optional Parameters

These parameters can be used with the main actions to fine-tune behavior:

*   **`--interval s`**: Sets the check interval for swap usage when in `--get` mode.
    *   **Default:** 10 seconds
    *   **Example:** `--interval 5` checks every 5 seconds.
*   **`--hl_analyze m`**: Sets the highlighting threshold for ebuilds in the `--analyze` report.
    *   Ebuilds that caused swapping for at least this many minutes will be highlighted (e.g., in red).
    *   **Default:** 15 minutes
    *   **Example:** `--hl_analyze 30` highlights ebuilds that swapped for 30 minutes or more.
*   **`--hl_list s`**: Sets the highlighting threshold for individual log entries when using `--list`.
    *   If there are this many consecutive log entries showing an increase in swap usage, that sequence will be highlighted.
    *   **Default:** 3 consecutive logs
    *   **Example:** `--hl_list 5` highlights sequences where swap increased for 5 or more consecutive measurements.
*   **`--hl_only`**: When used with `--analyze` or `--list`, this flag filters the output to display *only* the highlighted records, omitting all others.
    *   **Default:** `False` (all records are shown, with highlights)
    *   **Example:** `swapping_ebuilds --analyze --hl_analyze 10 --hl_only` would only show ebuilds that swapped for 10 minutes or more.
*   **`--version`**: Displays the version number of the `swapping_ebuilds` script and then exits.

### Examples

Here are some common usage examples:

*   **Start monitoring and logging swap usage:**
    ```bash
    swapping_ebuilds --get
    ```
    To run this in the background, you might use `nohup swapping_ebuilds --get &` or a systemd service.

*   **Monitor swap usage every 5 seconds:**
    ```bash
    swapping_ebuilds --get --interval 5
    ```

*   **Analyze the collected logs and view a report:**
    ```bash
    swapping_ebuilds --analyze
    ```

*   **Analyze logs, highlighting ebuilds that swapped for at least 30 minutes:**
    ```bash
    swapping_ebuilds --analyze --hl_analyze 30
    ```

*   **List all raw log entries:**
    ```bash
    swapping_ebuilds --list
    ```

*   **List raw log entries, highlighting sequences of 5 or more consecutive swap events:**
    ```bash
    swapping_ebuilds --list --hl_list 5
    ```

*   **Show only highlighted records when analyzing:**
    ```bash
    swapping_ebuilds --analyze --hl_only
    ```

*   **Show only highlighted records when listing:**
    ```bash
    swapping_ebuilds --list --hl_only
    ```

*   **Clean (delete) the log file:**
    ```bash
    swapping_ebuilds --clean
    ```

*   **Display the script version:**
    ```bash
    swapping_ebuilds --version
    ```


## Linux installation

### Gentoo Linux

The ebuild can be found in the `myportage` repository:
`https://github.com/turulomio/myportage/tree/master/app-admin/swapping_ebuilds`
