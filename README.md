# Graph-Visualization-Project-SOK

Team number 6 consists of four members:
Kristina Pavličević, Neda Simonić, Milica Ćorilić and Sofija Zorić

## Workspace storage

The Django application can create one `WorkspaceManager` in its
`AppConfig.ready()` with an `InMemoryGraphRepository` and share it with the
platform service. The manager is process-local, so workspaces are lost when
the process restarts. If the web app serves multiple independent users, keep
a separate manager for each user session.
