import os
import subprocess

DEFAULT_TIMEOUT = 30  # seconds
MAX_OUTPUT = 10_000  # characters sent back to Claude

READ_FILE = {
    "name": "read_file",
    "description": "Read a file and return its contents as text. "
    "Use this when you want to know what's inside a file.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file, relative to the current folder.",
            }
        },
        "required": ["path"],
    },
}

LIST_FOLDER = {
    "name": "list_folder",
    "description": "List what's in a folder, one name per line. Folders end with a slash. "
    "Not recursive: to see inside a subfolder, call it again with that subfolder. "
    "Hidden entries (starting with a dot, e.g. .gitignore) are left out unless you ask for them.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Folder to list, relative to the current folder. Defaults to the current folder.",
            },
            "include_hidden": {
                "type": "boolean",
                "description": "Also list hidden entries. Defaults to false.",
            },
        },
    },
}

EDIT_FILE = {
    "name": "edit_file",
    "description": "Edit a file by replacing old_str with new_str. "
    "old_str must appear exactly once in the file, so include enough surrounding lines to make it unique. "
    "Read the file first, so old_str matches it exactly, including whitespace. "
    "To create a new file, pass an empty old_str and the whole content as new_str.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file, relative to the current folder.",
            },
            "old_str": {
                "type": "string",
                "description": "The exact text to replace. Empty to create a new file.",
            },
            "new_str": {
                "type": "string",
                "description": "The text to put in its place.",
            },
        },
        "required": ["path", "old_str", "new_str"],
    },
}

DELETE_FILE = {
    "name": "delete_file",
    "description": "Delete a file."
    "Use this when you need to find the file.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file, relative to the current folder.",
            },
        },
        "required": ["path"],
    },
}

COMMIT_CHANGES = {
    "name": "commit_changes",
    "description": "Executes a local shell command in the project directory. Use this to 'git add' and 'git commit'."
    "Use this to generate a logical commit message.",
    "input_schema": {
        "type": "object",
        "properties": {
            "commit_message": {
                "type": "string",
                "description": "The name of the commit",
            },
        },
        "required": ["commit_message"],
    },
}

CHECK_CHANGES = {
    "name": "check_changes",
    "description": "Executes a local shell command in the project directory. Use this to check for file changes using 'git status' and 'git diff'.",
    "input_schema": {
        "type": "object",
        "properties": {} 
    }
}
RUN_PROGRAM = {
    "name": "run_program",
    "description": "Run a program on the user's computer and return its output (stdout and stderr together) "
    "and its exit code. The program runs in the current folder. "
    "There is no shell: give the program and each of its arguments separately, "
    "so pipes, redirects, globs and `cd` do not work. "
    "A non-zero exit code is not an error of this tool: it comes back with the output, so you can read it. "
    "Programs that run longer than the timeout are killed.",
    "input_schema": {
        "type": "object",
        "properties": {
            "program": {
                "type": "string",
                "description": "The program to run, e.g. `python` or `git`.",
            },
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "The arguments, one string each, e.g. [\"-m\", \"pytest\", \"-q\"]. Defaults to none.",
            },
            "timeout_seconds": {
                "type": "integer",
                "description": f"Seconds to wait before killing the program. Defaults to {DEFAULT_TIMEOUT}.",
            },
        },
        "required": ["program"],
    },
}

def check_changes():
    status = subprocess.run(["git", "status"], capture_output=True)
    diff = subprocess.run(["git", "diff"], capture_output=True)
    return f"""Checked file changes:
        \n status: {status} 
        \n diff: {diff}"""

def commit_changes(commit_message):
    token = os.environ["GITHUB_TOKEN"]
    remote = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()

    subprocess.run(
        ['git', 'config', '--global', 'user.name', 'Claude'],
        check=True
    )
    subprocess.run(
        ['git', 'config', '--global', 'user.email', 'claude@api.com'],
        check=True
    )
    print(subprocess.run(["git", "add", "."], capture_output=True))
    print(subprocess.run(["git", "commit", "-m", f"{commit_message}"], capture_output=True, text=True))

    #token = os.environ.get("GITHUB_TOKEN")
    #repo_url = f"https://{token}@://github.com"
    env = os.environ.copy()
    if remote.startswith("https://github.com/"):
        authenticated_url = remote.replace(
            "https://github.com/",
            f"https://x-access-token:{token}@github.com/",
            1
        )
    else:
        raise ValueError(
            "Expected an HTTPS GitHub origin URL"
        )
    # result = subprocess.run(["git", "push", "origin", "HEAD"], capture_output=True)
    subprocess.run(
        ["git", "push", authenticated_url, "HEAD"],
        check=True,
        env=env
    )
    # print(result)

    #if result.returncode == 0:
    #    print("Success:", result.stdout)
    #else:
    #    clean_error = result.stderr.replace(token, "********")
    #    print("Failed:", clean_error)

    return "Files commited and pushed"
    
def delete_file(path):
    if not os.path.exists(path):
        return f"{path} does not exist"
    
    os.remove(path)
        
    return f"Deleted the file at {path}"
        
def read_file(path):
    with open(path) as f:
        return f.read()

def list_folder(path=".", include_hidden=False):
    names = sorted(os.listdir(path))
    if not include_hidden:
        names = [name for name in names if not name.startswith(".")]
    if not names:
        return "(empty folder)"
    return "\n".join(
        name + "/" if os.path.isdir(os.path.join(path, name)) else name for name in names
    )

def edit_file(path, old_str, new_str):
    if old_str == new_str:
        raise ValueError("old_str and new_str are the same")

    if old_str == "":
        if os.path.exists(path):
            raise ValueError(f"{path} already exists; to change it, give the text to replace")
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w") as f:
            f.write(new_str)
        return f"Created {path}"

    with open(path) as f:
        content = f.read()

    count = content.count(old_str)
    if count == 0:
        raise ValueError(f"old_str not found in {path}")
    if count > 1:
        raise ValueError(f"old_str appears {count} times in {path}; include more context to make it unique")

    with open(path, "w") as f:
        f.write(content.replace(old_str, new_str))
    return f"Edited {path}"

def run_program(program, args=None, timeout_seconds=DEFAULT_TIMEOUT):
    command = [program] + list(args or [])
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,  # a program that waits for input must not hang Sancho
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as e:
        output = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        raise RuntimeError(
            f"{program} was killed after {timeout_seconds} seconds. Output so far:\n{_shorten(output)}"
        )

    return f"{_shorten(completed.stdout) or '(no output)'}\n[exit code {completed.returncode}]"

def _shorten(text):
    """Keep the start and the end of long output: the start says what ran, the end usually says what failed."""
    if len(text) <= MAX_OUTPUT:
        return text
    half = MAX_OUTPUT // 2
    return text[:half] + f"\n... ({len(text) - MAX_OUTPUT} characters left out) ...\n" + text[-half:]



NOTREAD = ["edit_file", "delete_file", "commit_changes","run_program"]
DEFINITIONS = [
    READ_FILE, 
    LIST_FOLDER, 
    EDIT_FILE, 
    DELETE_FILE, 
    COMMIT_CHANGES,
    CHECK_CHANGES,
    RUN_PROGRAM
    ]
FUNCTIONS = {
    READ_FILE["name"]: read_file, 
    LIST_FOLDER["name"]: list_folder, 
    EDIT_FILE["name"]: edit_file, 
    DELETE_FILE["name"]: delete_file,
    COMMIT_CHANGES["name"]: commit_changes,
    CHECK_CHANGES["name"]: check_changes,
    RUN_PROGRAM["name"]: run_program
    }

def run(tool_calls):
    results = []
    readOnly = True
    for call in tool_calls:
        print(f"\033[90m🔧 {call.name}({call.input})\033[0m")
        print(call.name)
        if NOTREAD.__contains__(call.name):
            readOnly = False

    if not readOnly:
        user_input = input("Confirm action(s): [y/n]")
        
        if not user_input == "y":
            return [{
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": "User chose to not execute the actions and asked for your list of tools",
                    }]

    for call in tool_calls:
        try:
            # print(f"\033[90m🔧 {call.name}({call.input})\033[0m")

            function = FUNCTIONS[call.name]
            result = function(**call.input)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": result,
                }
            )
        except Exception as e:
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": str(e),
                    "is_error": True,
                }
            )

    return results
