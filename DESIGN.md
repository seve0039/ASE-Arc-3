# ASE-Arc-3
<!-- the design log. Every decision you made and why, everything that surprised you, everything that failed. Short entries, written as they happen.-->
This design log only includes features that were added additionally to the agent other than the minimum features. 
## Planner + Confirmation
The planner provides lists of changes to the user that the agent may plan to do. This requires confirmation from the user before the agent is able to do those changes. This is to give the user more control over what the agent does, in case it does an action that the user regrets e.g. deleting an important file. As of now, it does not provide a full list at once as its actions depend on each other. 

## Tool for deletion of files
The agent can now delete files for cleaning up the repository from messy or conflicting files. Confirmation is also needed here to ensure that important files are not deleted by accident. 

## Token safe guarding
To ensure that the agent does not spend too many tokens, we limit the tokens used by the agent by notifying the user whenever the current token count is over a specific amount. This requires the user to confirm whether they want to continue.  

## Check file changes
To allow the agent to run commands, such as 'git status' and 'git diff' to allow it to view the current file changes. This is to assist the agent in making logical commit messages, as well as knowing exactly what changes have been made. 

## Commit and push file changes
The agent can commit and push file changes to streamline the development. This currently only works for its own repository. 
