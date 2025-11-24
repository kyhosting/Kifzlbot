# KIFZL DEV BOT

## Overview

A comprehensive Telegram bot for contact management and file conversion operations. The bot provides role-based access control (FREE/VIP/PREMIUM/OWNER) with various utilities for manipulating contact files, including format conversions (TXT, VCF, XLSX), file splitting/merging, and contact creation tools. Built with Python using the python-telegram-bot library.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Library**: python-telegram-bot v20.7
- **Architecture Pattern**: Modular command handlers with conversation flows
- **Rationale**: Separates concerns by organizing each feature into its own module, making the codebase maintainable and scalable. Uses ConversationHandler for multi-step user interactions.

### User Management & Authorization
- **Access Control**: Role-based system with 4 tiers (FREE, VIP, PREMIUM, OWNER)
- **User Persistence**: JSON file-based storage (`users.json`)
- **Session Management**: Conversation states tracked via `sessions.json`
- **Rationale**: Simple file-based storage is sufficient for bot-scale operations without the overhead of a database. Role hierarchy allows progressive feature unlocking.

### Data Storage
- **Primary Storage**: JSON files for all persistent data
  - `users.json`: User profiles, roles, expiry dates, operation counts
  - `redeem.json`: VIP/Premium redemption codes
  - `admins.json`: Admin contact data
  - `sessions.json`: Active conversation states
- **Rationale**: Lightweight, human-readable, and sufficient for the scale. No complex queries needed, making JSON ideal over a relational database.

### File Processing Pipeline
- **Supported Formats**: TXT, VCF (vCard), XLSX/XLS
- **Processing Libraries**:
  - `vobject`: VCF file parsing and generation
  - `pandas` + `openpyxl`: Excel file handling
  - Native Python: Text file operations
- **Workflow**: Download → Process → Generate → Upload → Cleanup
- **Rationale**: Each library is industry-standard for its format. Temporary file approach prevents memory issues with large files.

### Feature Access Gating
- **FREE Tier**: Basic read operations (count contacts, check names, view status)
- **VIP Tier**: All conversions, file operations, split/merge
- **PREMIUM Tier**: Extended duration access to VIP features
- **OWNER Tier**: User management, redeem code generation, statistics
- **Rationale**: Freemium model encourages upgrades while providing value to all users. Owner controls maintain security and prevent abuse.

### Auto-Verification System
- **Trigger**: Users joining specific VIP groups
- **Grant**: Automatic 7-day VIP access
- **Implementation**: ChatMemberUpdated event handler checks group membership
- **Rationale**: Growth mechanism that rewards community participation with temporary premium access.

### Redeem Code System
- **Code Generation**: Random 12-character alphanumeric strings
- **Properties**: Role assignment, duration, code expiration, single-use
- **Validation**: Checks code validity, expiration, and usage status
- **Rationale**: Provides flexible access distribution method for promotions and partnerships.

### Command Flow Architecture
- **Pattern**: ConversationHandler with state machines
- **States**: Multi-step input collection (file → filename → options → process)
- **Cancellation**: Universal "❌ BATAL ❌" button in all flows
- **Rationale**: Guides users through complex operations step-by-step, reducing errors and improving UX.

### Security & Protection
- **Anti-Theft**: Creator attribution enforcement in README
- **Owner Validation**: Hard-coded OWNER_ID for administrative functions
- **Access Checks**: Pre-execution role validation on all protected commands
- **Rationale**: Prevents unauthorized access and maintains attribution to original creator.

### Expiry Management
- **Background Task**: Periodic checker for expired VIP/PREMIUM users
- **Notifications**: Automated messages when access expires
- **Auto-Downgrade**: Expired users revert to FREE tier
- **Rationale**: Ensures fair access control and encourages renewals through timely notifications.

## External Dependencies

### Telegram Bot API
- **Service**: Telegram Bot Platform
- **Purpose**: Primary user interface and interaction layer
- **Integration**: Via `python-telegram-bot` wrapper library
- **Authentication**: Bot token (environment variable or configuration)

### Python Libraries
- **python-telegram-bot (v20.7)**: Core bot framework and API wrapper
- **vobject (v0.9.6.1)**: VCF/vCard file parsing and generation
- **pandas (v2.0.3)**: Excel file data manipulation
- **openpyxl (v3.1.2)**: XLSX file reading/writing
- **python-dateutil (v2.8.2)**: Date/time parsing and manipulation

### File System
- **Purpose**: Temporary file storage during processing operations
- **Pattern**: Create temp files → Process → Send result → Delete temp files
- **Location**: Bot's working directory with user_id-based naming

### VIP Groups (Community Integration)
- **Groups**: 
  - https://t.me/agentviber12
  - https://t.me/channelviber
- **Purpose**: Auto-grant VIP access to members (7-day trial)
- **Implementation**: ChatMemberUpdated webhook integration

### No Database Required
- **Note**: Current implementation uses JSON file storage exclusively. No PostgreSQL, MySQL, or other database systems are configured. Future scaling may require database integration, but current architecture supports migration without major refactoring.