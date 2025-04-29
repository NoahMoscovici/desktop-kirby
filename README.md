# Desktop Kirby <img src="animations/sleep%20-%20120.gif" alt="Sleeping Kirby" width="60" style="vertical-align: middle;" />

A delightful desktop companion inspired by Desktop Goose, featuring Kirby! This application creates an interactive Kirby that floats around your desktop, performing various cute animations and interactions. 

[📥 Download Windows Installer](install/desktop%20kirby%20installer.exe)

[📋 Installation Guide](#installation-windows)

[💻 Development Setup](#development-setup)

## Examples

![Example clip 1](examples/clip1.gif)
![Example clip 2](examples/clip2.gif)

## Features

- Adorable Kirby animations created in Blender
- Multiple interactive behaviors:
  - Walking and flying around your desktop
  - Sleeping when idle
  - Eating your cursor
  - Dragging windows around
  - And more surprises!
- System tray integration for easy control

## Installation (Windows)

### Option 1: Using the Installer

1. Download the installer from the `/install` folder: [desktop kirby installer.exe](install/desktop%20kirby%20installer.exe)
2. Run the installer executable
3. Follow the installation wizard instructions
4. Launch Desktop Kirby from your Start Menu or desktop shortcut

### Option 2: Building from Source

To build your own Windows executable:

1. Install Python 3.x
2. Install required dependencies:
   ```bash
   pip install tkinter auto-py-to-exe
   ```
3. Install NSIS (Nullsoft Scriptable Install System)
4. Run auto-py-to-exe:
   ```bash
   auto-py-to-exe
   ```
5. In the auto-py-to-exe GUI:
   - Select `main.pyw` as your script
   - Choose "One File" and "Window Based"
   - Add the following folders as additional files:
     - `animations/`
     - `images/`
     - `lib/`
   - Convert to executable
6. Use NSIS to create an installer with the generated executable

## Development Setup

To run Desktop Kirby in development mode:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/desktop-kirby.git
   cd desktop-kirby
   ```

2. Install Python 3.x if you haven't already

3. Install required dependencies:
   ```bash
   pip install tkinter
   ```

4. Run the application:
   ```bash
   python main.pyw
   ```

## Project Structure

- `main.pyw` - Main application file
- `animations/` - Kirby animation files
- `images/` - Static image assets
- `lib/` - Helper utilities and functions
- `install/` - Installation files and executable

## Known Issues

- Currently only fully functional on Windows due to Tkinter transparency limitations on macOS
- Some window management features may behave differently across Windows versions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- All Kirby animations (except those in `images/`) were created by the author using Blender
- Original concept inspired by Desktop Goose
- Built with Python and Tkinter
