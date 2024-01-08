#!/bin/bash
set +e  # Continue on errors

# Install project dependencies
echo "Ensuring dependencies installed..."
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo "Done."

COLOR_BLUE="\033[0;94m"
COLOR_GREEN="\033[0;92m"
COLOR_RESET="\033[0m"

# Print useful output for user
echo -e "${COLOR_BLUE}

████████▄     ▄████████    ▄████████    ▄██████▄  ███    █▄   ▄█          ▄████████ 
███   ▀███   ███    ███   ███    ███   ███    ███ ███    ███ ███         ███    ███ 
███    ███   ███    ███   ███    ███   ███    █▀  ███    ███ ███         ███    ███ 
███    ███  ▄███▄▄▄▄██▀   ███    ███  ▄███        ███    ███ ███         ███    ███ 
███    ███ ▀▀███▀▀▀▀▀   ▀███████████ ▀▀███ ████▄  ███    ███ ███       ▀███████████ 
███    ███ ▀███████████   ███    ███   ███    ███ ███    ███ ███         ███    ███ 
███   ▄███   ███    ███   ███    ███   ███    ███ ███    ███ ███▌    ▄   ███    ███ 
████████▀    ███    ███   ███    █▀    ████████▀  ████████▀  █████▄▄██   ███    █▀  
             ███    ███                                      ▀                      

Using retrieval augmented generation (RAG) to help ChatGPT reference specific parts of Bram Stoker's Dracula.${COLOR_RESET}


Welcome to your development container!

This is how you can work with it:
- Files will be synchronized between your local machine and this container
- Ensure your \`${COLOR_GREEN}OPENAI_API_KEY${COLOR_RESET}\` env variable is set before loading the chat
- Run \`${COLOR_GREEN}python dragula.py${COLOR_RESET}\` to start the chat
"

# Set terminal prompt
export PS1="\[${COLOR_BLUE}\]devspace\[${COLOR_RESET}\] ./\W \[${COLOR_BLUE}\]\\$\[${COLOR_RESET}\] "
if [ -z "$BASH" ]; then export PS1="$ "; fi

# Include project's bin/ folder in PATH
export PATH="./bin:$PATH"

# Open shell
bash --norc
