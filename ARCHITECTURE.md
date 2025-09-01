# Arquitectura del Proyecto

## Descripción General

Este proyecto es una aplicación FastAPI que implementa arquitectura limpia (Clean Architecture), separando las preocupaciones en capas para mantener la independencia y testabilidad.

## Capas de Arquitectura

### 1. Capa de Dominio (Domain Layer)
- **Ubicación**: `src/app/domain/`
- **Propósito**: Contiene la lógica de negocio central, independiente de frameworks externos.
- **Directorios**:
  - `entities/`: Entidades del dominio (ej. User)
  - `enums/`: Enumeraciones (ej. UserRole)
  - `exceptions/`: Excepciones específicas del dominio
  - `ports/`: Interfaces para dependencias externas (ej. PasswordHasher, UserIdGenerator)
  - `services/`: Servicios de dominio puro
  - `value_objects/`: Objetos de valor (ej. UserId, Username, RawPassword)

### 2. Capa de Aplicación (Application Layer)
- **Ubicación**: `src/app/application/`
- **Propósito**: Define los casos de uso y orquesta la lógica de aplicación.
- **Directorios**:
  - `commands/`: Comandos de aplicación (ej. ActivateUser, ChangePassword, GrantAdmin)
  - `common/`: Elementos compartidos (excepciones, puertos, modelos de consulta, parámetros de consulta, servicios comunes)
  - `features/`: Características específicas (meeting, user)

### 3. Capa de Infraestructura (Infrastructure Layer)
- **Ubicación**: `src/app/infrastructure/`
- **Propósito**: Implementa las dependencias externas y adaptadores.
- **Directorios**:
  - `adapters/`: Adaptadores concretos (ej. PasswordHasherBcrypt, MainFlusherSqla, MainTransactionManagerSqla)
  - `auth/`: Autenticación y manejo de sesiones
  - `diator/`: Contenedor de dependencias
  - `exceptions/`: Excepciones de infraestructura
  - `persistence_sqla/`: Persistencia con SQLAlchemy (mappings, config, provider, registry, alembic)

### 4. Capa de Presentación (Presentation Layer)
- **Ubicación**: `src/app/presentation/`
- **Propósito**: Maneja la interfaz de usuario y entrada/salida.
- **Directorios**:
  - `http/`: Controladores HTTP, manejadores de autenticación, errores

### 5. Configuración y Setup
- **Ubicación**: `src/app/setup/`
- **Propósito**: Configura la aplicación y la inyección de dependencias.
- **Directorios**:
  - `config/`: Configuraciones (base de datos, logs, seguridad, settings)
  - `ioc/`: Proveedores de inyección de dependencias para cada capa (application, domain, infrastructure, presentation)

### Otros Directorios Relevantes
- `tests/`: Pruebas unitarias, de integración y rendimiento
- `config/`: Configuraciones por entorno (dev, local, prod)
- `docs/`: Documentación y diagramas de arquitectura
- `scripts/`: Scripts auxiliares (ej. para Dishka, Makefile)