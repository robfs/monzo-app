# Monzo App v2 - Reactive Financial Analytics

## Overview

This is a completely rewritten version of the Monzo financial analytics application, built with modern reactive architecture principles and best practices. Unlike v1, this version demonstrates proper separation of concerns, centralized state management, and reactive data flow throughout the application.

## Key Improvements Over v1

### ✨ Architecture Improvements

- **Centralized State Management**: Single source of truth via `AppState`
- **Event-Driven Architecture**: Proper event bus for component communication
- **Service Layer Pattern**: Separate services for settings, data, and state
- **Reactive Components**: Automatic updates via reactive properties
- **Proper Separation of Concerns**: Clear boundaries between UI, business logic, and data

### 🔧 Technical Features

- **App-Wide Settings**: Settings are no longer tied to individual screens
- **Reactive Labels**: Specialized widgets that automatically update with state changes
- **Event Bus System**: Decoupled communication between components
- **Mock Data Service**: Demonstrates data flow without external dependencies
- **Configurable Modals**: Reusable modal screens with callback support
- **State-Aware Widgets**: Base classes that automatically sync with app state

## Architecture Overview

```
src/v2/
├── core/                   # Core services and state management
│   ├── state.py           # Central application state
│   ├── settings.py        # Settings service with reactive updates
│   ├── data_service.py    # Mock data service for demonstration
│   ├── events.py          # Event bus system
│   └── __init__.py
├── screens/               # Application screens
│   ├── base.py           # Base screen classes
│   ├── dashboard.py      # Main dashboard with reactive components
│   ├── settings.py       # Settings configuration modal
│   ├── exclusions.py     # Category exclusions modal
│   └── __init__.py
├── widgets/               # Reusable UI components
│   ├── base.py           # Base widget classes
│   ├── reactive_label.py # Self-updating label components
│   └── dashboard/        # Dashboard-specific widgets
│       ├── balance_card.py
│       ├── charts.py
│       ├── tables.py
│       └── info_cards.py
├── utils/                 # Utility functions
│   └── helpers.py
├── assets/
│   └── styles.tcss       # Application styles
├── app.py                # Main application
├── run.py                # Entry point script
└── README.md             # This file
```

## Key Components

### Core Services

1. **AppState** (`core/state.py`): Central reactive state management
2. **SettingsService** (`core/settings.py`): App-wide configuration management
3. **DataService** (`core/data_service.py`): Mock data provider with realistic simulation
4. **EventBus** (`core/events.py`): Event-driven communication system

### Reactive Components

- **ReactiveLabel**: Base label that updates automatically
- **StateLabel**: Label bound to specific state properties
- **CurrencyLabel**: Specialized currency formatting
- **CounterLabel**: Count display with pluralization
- **StatusLabel**: Status indicators with mapping
- **TimeLabel**: Time/date formatting

### Smart Widgets

- **StateAwareWidget**: Base for widgets that respond to state changes
- **DataWidget**: Base for data-driven components
- **BalanceCard**: Shows current balance with status
- **Charts**: Reactive spending analysis visualizations
- **Tables**: Dynamic data tables with exclusion support

## Running the Application

### Prerequisites

- Python 3.8+
- Textual library (`pip install textual`)

### Quick Start

```bash
# Navigate to the v2 directory
cd monzo-app/src/v2

# Run the application
python run.py

# Alternative: run directly
python app.py
```

### Development Mode

For development with enhanced logging:

```bash
# Run with debug logging
TEXTUAL_LOG=debug python run.py

# View logs in separate terminal
textual console
```

## Key Bindings

| Key | Action | Description |
|-----|--------|-------------|
| `D` | Dashboard | Return to main dashboard |
| `S` | Settings | Open settings configuration |
| `E` | Exclusions | Manage category exclusions |
| `R` | Refresh | Refresh all data |
| `Q` / `Ctrl+C` | Quit | Exit application |
| `?` | Help | Show help information |

### Dashboard Additional Keys

| Key | Action | Description |
|-----|--------|-------------|
| `T` | Tables | Focus on data tables |
| `C` | Charts | Focus on chart widgets |
| `D` | Debug | Toggle debug panels |

## Reactive Data Flow

The application demonstrates reactive programming principles:

1. **State Changes**: Central state updates trigger events
2. **Event Propagation**: Events flow through the event bus
3. **Component Updates**: Widgets listen for relevant events
4. **UI Refresh**: Components update automatically without manual intervention

### Example Flow

```
User Changes Settings 
    ↓
SettingsService.update()
    ↓
Event: SETTINGS_CHANGED
    ↓
AppState syncs from service
    ↓
Reactive properties update
    ↓
UI components refresh automatically
```

## Mock Data Features

Since this is a demonstration version, realistic mock data is generated:

- **Transactions**: 50-150 mock transactions over 90 days
- **Categories**: 13 different spending categories
- **Merchants**: 20+ realistic merchant names
- **Balance Calculation**: Computed from transaction history
- **Statistics**: Monthly spending, category breakdowns, trends

## Configuration

The application supports various configuration options:

### Settings

- **Spreadsheet ID**: Mock Google Sheets integration
- **Credentials Path**: File path validation
- **Pay Day Configuration**: First/last/specific day of month
- **Theme Selection**: Multiple UI themes
- **Auto-refresh**: Configurable refresh intervals

### Exclusions

- **Category Filtering**: Exclude categories from analysis
- **Dynamic Updates**: Charts recalculate when exclusions change
- **Persistent Settings**: Exclusions saved in app state

## Educational Features

This version is designed to demonstrate:

### Reactive Architecture
- Centralized state management
- Event-driven updates
- Automatic UI synchronization

### Best Practices
- Separation of concerns
- Service layer pattern
- Type hints and documentation
- Error handling and logging

### Component Design
- Reusable widget base classes
- Configurable and extensible components
- Proper inheritance hierarchies

## Extending the Application

### Adding New Widgets

1. Inherit from `StateAwareWidget` or `DataWidget`
2. Override reactive event handlers
3. Use reactive labels for automatic updates

```python
class MyWidget(StateAwareWidget):
    def on_data_updated(self, event: AppEvent):
        # React to data changes
        pass
```

### Adding New Screens

1. Inherit from `BaseScreen` or `StateAwareScreen`
2. Register in app's `SCREENS` dictionary
3. Add key binding if needed

### Custom Reactive Labels

```python
class CustomLabel(StateLabel):
    def __init__(self, **kwargs):
        super().__init__(
            state_key="my_property",
            format_func=self.custom_formatter,
            **kwargs
        )
    
    def custom_formatter(self, value):
        return f"Custom: {value}"
```

## Differences from v1

| Aspect | v1 | v2 |
|--------|----|----|
| State Management | Scattered reactive props | Centralized AppState |
| Settings | Screen-specific | App-wide service |
| Communication | Direct method calls | Event bus |
| Updates | Manual refresh calls | Automatic reactive updates |
| Data Flow | Tightly coupled | Loosely coupled via events |
| Extensibility | Hard to extend | Modular and extensible |
| Testing | Difficult to test | Service layer testable |

## Performance Considerations

- **Event Batching**: Multiple rapid events are handled efficiently
- **Lazy Loading**: Components only update when mounted
- **Memory Management**: Weak references prevent memory leaks
- **Thread Safety**: Background data refresh in separate threads

## Logging and Debugging

The application includes comprehensive logging:

- **Service Events**: All state changes logged
- **Component Lifecycle**: Mount/unmount events
- **Data Operations**: Query execution and results
- **Error Handling**: Detailed error messages with context

Enable debug mode with the `D` key on the dashboard to see:
- Real-time system information
- Event log with timestamps
- State change history
- Performance metrics

## Future Enhancements

Potential improvements for this architecture:

1. **Persistence Layer**: Save state to disk
2. **Plugin System**: Dynamic component loading
3. **Real Data Integration**: Connect to actual APIs
4. **Advanced Charts**: More sophisticated visualizations
5. **Export Features**: PDF/CSV export capabilities
6. **Multi-user Support**: User-specific settings
7. **Caching Layer**: Intelligent data caching
8. **Real-time Updates**: WebSocket integration

## Conclusion

This v2 implementation showcases modern reactive architecture principles in a terminal-based application. The separation of concerns, event-driven design, and reactive components create a maintainable and extensible codebase that serves as an excellent foundation for complex financial analytics applications.

The reactive data flow ensures that all components stay synchronized automatically, reducing bugs and improving user experience. The modular design makes it easy to add new features without affecting existing functionality.