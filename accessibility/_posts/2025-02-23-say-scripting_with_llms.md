---
layout: post
title:  "Say Scripting with LLMs"
date:   2025-02-23 00:00:30 -0500
tags:   accessibility llm terminal
---

How does one get the terminal to speak output?

There are various ways to achieve the goal with accessibility tools (e.g. screen readers like VoiceOver on macOS, or libraries like [emacspeak](https://github.com/tvraman/emacspeak)). But suppose we want something simple...

## Say

On macOS, the built-in text-to-speech (TTS) utility is `say`:

`say hello`

... says hello. There are a few simple flags to control the speech rate, voice, etc. 

To print command results to the terminal while also calling `say`, we can use `tee` to duplicate the input:

`date | tee /dev/tty | say`

An alias like `alias dates='date | tee /dev/tty | say'` can be convenient, but it doesn't take additional arguments to the original command. Alternatively, we can define multiple aliases as functions (e.g. as a script to call from `~/.zshrc`).

```sh
#!/bin/zsh

typeset SPEECH_RATE=300
typeset -A saycommands
saycommands=(
    lss "ls -1"
    pwds "pwd"
    dates "date"
)

for key in ${(k)saycommands}; do
    command="${saycommands[$key]}"
    eval "
        function ${key} {
            ${command} \"\$@\" | tee /dev/tty | say -r \${SPEECH_RATE}
        }
    "
done

echo "Say-enabled commands: ${(k)saycommands}"
```

## Say Mode? Asking an LLM

For a more general solution, maybe we want the terminal to always speak output. And for non-experts in zshell, maybe we want help from an LLM.

The LLMs tried are: (1) ChatGPT 4o in the macOS desktop app: (2) Mistral's default model in the web UI. In both cases, the initial prompt is simple: "In MacOS ZSH, I want to intercept every shell output and also speak it aloud with `say -r 300`".

Interestingly, ChatGPT didn't generate working code even after a few iterations, while Mistral quickly got something working, albeit a bit buggy. This is Mistral's initial working version, which speaks the output once but prints it three times: [link to gist](https://gist.github.com/tkuriyama/ef28d12e496b8670d5bee74f787f4f9a).

I didn't spend too much time engineering the prompts, but toggling back and forth between ChatGPT and Mistral, I found that:
- neither model could fully and independently resolve the triple-printing issue
- both models are better at debugging than generating code
- the differential diagnosis between models (i.e. comparing their outputs) is useful

Overall, the results were roughly on par with expectations. For a modest task, the LLMs can do a good draft, allowing the human programmer to focus on refining the results. (Also, the time-savings were meaningful in this instance, since I know very little about shell/zshell scripting). And although by no means a rigorous comparison, I preferred the speed and quality of Mistral.

This is the final, working version, which allows say mode to be toggled in the terminal with `saymode on` and `saymode off` and includes a prompt indicator. It's not particularly elegant and lacks some obvious usability features, but it works as a proof of concept. 

```sh
#!/bin/zsh

typeset -g SAYMODE_ENABLED=false
typeset -g LAST_COMMAND_OUTPUT=""
typeset -g DEFAULT_PROMPT="$PROMPT"

################################################################################


function speak_last_output() {
    if [[ $SAYMODE_ENABLED == true && -n "$LAST_COMMAND_OUTPUT" ]]; then
        echo "$LAST_COMMAND_OUTPUT    " | say -r 300
        LAST_COMMAND_OUTPUT=""
    fi
}

function capture_output() {
    LAST_COMMAND_OUTPUT=$(eval "$1" 2>&1)
    return ${PIPESTATUS[0]}
}

################################################################################

function preexec() {
    # Check if the command is not empty
    if [[ -n "$1" && $SAYMODE_ENABLED == true ]]; then
        capture_output "$1"
        # Prevent the original command from being executed
        return 1
    fi
}

preexec_functions+=(preexec)
precmd_functions+=(speak_last_output)

################################################################################

function saymode_on() {
    SAYMODE_ENABLED=true
    PROMPT="%K{green}SAYMODE%k $DEFAULT_PROMPT"
    echo "Say mode enabled."
}

# Define the vmode off command
function saymode_off() {
    PROMPT="$DEFAULT_PROMPT"
    echo "Say mode disabled."
    SAYMODE_ENABLED=false
}

function saymode() {
    if [[ "$1" == "on" ]]; then
        saymode_on
    elif [[ "$1" == "off" ]]; then
        saymode_off
    else
        echo "Usage: vmode {on|off}"
    fi
}
```

## Can You Do Better?

Some usability improvements that come to mind:

- output can be automatically Limited in length
- commands can be whitelisted or blacklisted, since e.g. "vi" or "men" that start a new program or terminal paging mode are not compatible

What does a different model like Grok 3 think?

`I want you to comment on this Zsh Voice mode program. What are some good usability or feature enhancements to consider?`

Given a simple prompt like the above, Grok 3 yields an impressive answer.

- It identifies and solves both the above points without any specific prompting
- It provides several more suggestions and implements them with lucid explanations
- It identifies several nuances and gotchas, providing clear explanations 

Overall, it generates a more complex and feature-rich program ([copy-paste of the interactive session](https://gist.github.com/tkuriyama/bac9fb086bb5d56be7f736641af70a1d)). The revised script runs immediately without any modifications!

There are some oddities in the shell experience introduced by the more advanced functionality, which Grok 3 couldn't fully debug. so in the end I reverted to the original, simpler script and asked it to implement only a subset of improvements.

Here is the revised, working script, verbatim from Grok 3 (except for the whitelist of commands).

```zsh
# Global Variables
typeset -g SAYMODE_ENABLED=false              # Tracks whether Say Mode is enabled
typeset -g LAST_COMMAND_OUTPUT=""             # Stores the last command's output
typeset -g DEFAULT_PROMPT="$PROMPT"           # Stores the default prompt for restoration
typeset -gi SAYMODE_OUTPUT_LIMIT=${SAYMODE_OUTPUT_LIMIT:-500}  # Output limit in characters, default 100
typeset -g -A SAYMODE_COMMANDS=(
    ls 1 pwd 1 echo 1 date 1
    whoami 1 hostname 1 uname 1 which 1 where 1
    type 1 env 1 printenv 1 alias 1
    du 1 df 1 ll 1 la 1 lh 1 
)  # Whitelist of safe commands

# Function to speak the last command output
function speak_last_output() {
    if [[ $SAYMODE_ENABLED == true && -n "$LAST_COMMAND_OUTPUT" ]]; then
        local output_to_speak
        if [[ $SAYMODE_OUTPUT_LIMIT -gt 0 ]]; then
            output_to_speak="${LAST_COMMAND_OUTPUT:0:$SAYMODE_OUTPUT_LIMIT}"
        else
            output_to_speak="$LAST_COMMAND_OUTPUT"
        fi
        echo "$output_to_speak    " | say -r 300  # Preserve original rate of 300 wpm
        LAST_COMMAND_OUTPUT=""
    fi
}

# Function to capture command output
function capture_output() {
    LAST_COMMAND_OUTPUT=$(eval "$1" 2>&1)  # Capture stdout and stderr
    return ${PIPESTATUS[0]}  # Return the exit status of the command
}

# Pre-execution hook to process whitelisted commands
function preexec() {
    if [[ $SAYMODE_ENABLED == true && -n "$1" ]]; then
        local cmd_name=${1%%[[:space:]]*}  # Extract the first word of the command
        if [[ -n "${SAYMODE_COMMANDS[$cmd_name]}" ]]; then  # Check if command is in whitelist
            capture_output "$1"
            return 1  # Prevent original command execution
        fi
    fi
}

# Set up Zsh hooks
preexec_functions+=(preexec)      # Run preexec before each command
precmd_functions+=(speak_last_output)  # Run speak_last_output after each command

# Function to enable Say Mode
function saymode_on() {
    SAYMODE_ENABLED=true
    PROMPT="%K{green}SAYMODE%k $DEFAULT_PROMPT"  # Update prompt to indicate Say Mode
    echo "Say mode enabled."
}

# Function to disable Say Mode
function saymode_off() {
    PROMPT="$DEFAULT_PROMPT"  # Restore original prompt
    SAYMODE_ENABLED=false
    echo "Say mode disabled."
}

# Main Say Mode control function with toggle
function saymode() {
    if [[ "$1" == "on" ]]; then
        saymode_on
    elif [[ "$1" == "off" ]]; then
        saymode_off
    elif [[ -z "$1" ]]; then  # Toggle if no argument is provided
        if [[ $SAYMODE_ENABLED == true ]]; then
            saymode_off
        else
            saymode_on
        fi
    else
        echo "Usage: saymode {on|off}"  # Updated usage message
    fi
}


```
