# Project Architecture

## Overview

This project is a FastAPI application that implements Clean Architecture, separating concerns into layers to maintain independence and testability.

## Architecture Layers

### 1. Domain Layer
- **Location**: `src/app/domain/`
- **Purpose**: Contains core business logic, independent of external frameworks.
- **Directories**:
  - `entities/`: Domain entities (e.g. User)
  - `enums/`: Enumerations (e.g. UserRole)
  - `exceptions/`: Domain-specific exceptions
  - `ports/`: Interfaces for external dependencies (e.g. PasswordHasher, UserIdGenerator)
  - `services/`: Pure domain services
  - `value_objects/`: Value objects (e.g. UserId, Username, RawPassword)

### 2. Application Layer
- **Location**: `src/app/application/`
- **Purpose**: Defines use cases and orchestrates application logic.
- **Directories**:
  - `commands/`: Application commands (e.g. ActivateUser, ChangePassword, GrantAdmin)
  - `common/`: Shared elements (exceptions, ports, query models, query parameters, common services)
  - `features/`: Specific features (meeting, user)

### 3. Infrastructure Layer
- **Location**: `src/app/infrastructure/`
- **Purpose**: Implements external dependencies and adapters.
- **Directories**:
  - `adapters/`: Concrete adapters (e.g. PasswordHasherBcrypt, MainFlusherSqla, MainTransactionManagerSqla)
  - `auth/`: Authentication and session management
  - `diator/`: Dependency container
  - `exceptions/`: Infrastructure exceptions
  - `persistence_sqla/`: SQLAlchemy persistence (mappings, config, provider, registry, alembic)

### 4. Presentation Layer
- **Location**: `src/app/presentation/`
- **Purpose**: Handles user interface and input/output.
- **Directories**:
  - `http/`: HTTP controllers, authentication handlers, error handlers

### 5. Configuration and Setup
- **Location**: `src/app/setup/`
- **Purpose**: Configures the application and dependency injection.
- **Directories**:
  - `config/`: Configurations (database, logs, security, settings)
  - `ioc/`: Dependency injection providers for each layer (application, domain, infrastructure, presentation)

### Other Relevant Directories
- `tests/`: Unit, integration and performance tests
- `config/`: Environment-specific configurations (dev, local, prod)
- `docs/`: Documentation and architecture diagrams
- `scripts/`: Auxiliary scripts (e.g. for Dishka, Makefile)