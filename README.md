# Town Clock

## Overview

```mermaid
flowchart 
    A(Start) --> B{Bee}
    B --> C[End]
    B --> |Reasons| D(Alt End)
    C --> E(Goes to Website)
    C --> B

```

```mermaid
sequenceDiagram
    participant Client
    participant OAuth
    participant Server
    Client ->>+ OAuth: Request Access Token
    OAuth ->>- Client: Sends back token
    Client ->>+ Server: Requests resource
    Server ->>+ OAuth: Validates token
    OAuth ->>- Server: Token Valid
    Server ->>- Client: Sends resources

