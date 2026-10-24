# ASE-Arc-3
<!-- the design log. Every decision you made and why, everything that surprised you, everything that failed. Short entries, written as they happen.-->
This design log only includes features that were added additionally to the agent other than the minimum features. 
## Planner + Confirmation
The planner provides lists of changes to the user that the agent may plan to do. This requires confirmation from the user before the agent is able to do those changes. This is to give the user more control over what the agent does, in case it does an action that the user regrets e.g. deleting an important file. As of now, it does not provide a full list at once as its actions depend on each other. 

## Tool for deletion of files
The agent can now delete files for cleaning up the repository from messy or conflicting files. Confirmation is also needed here to ensure that important files are not deleted by accident. 

## Input token count

