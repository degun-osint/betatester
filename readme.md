# CTFd Beta Tester Plugin

A plugin for CTFd that allows administrators to designate certain users as beta testers who can access challenges before the official CTF start time.

## Support the Developer

If you find this plugin useful for your CTF events, consider supporting the developer:

<a href='https://ko-fi.com/D1D11CYJEY' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi1.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

## Overview

This plugin was originally developed for [Oscar Zulu](https://oscarzulu.org) to facilitate challenge testing before competitions begin, and is now being offered to the broader CTF creator community.

## Features

- Designate users as beta testers who can access challenges before the CTF starts
- Beta testers maintain regular user permissions without access to admin features
- Simple admin interface for managing beta testers
- Securely blocks beta testers from accessing admin routes
- Works with existing CTFd permission systems

## Installation

1. Create the plugin directory structure in your CTFd installation:
   ```bash
   mkdir -p /path/to/CTFd/plugins/betatester/templates
   ```

2. Copy the plugin files to the appropriate locations:
   - `__init__.py` → `/path/to/CTFd/plugins/betatester/`
   - `config.json` → `/path/to/CTFd/plugins/betatester/`
   - `betatesters.html` → `/path/to/CTFd/plugins/betatester/templates/`

3. Restart your CTFd instance to load the plugin.

## Usage

### Adding Beta Testers

1. In the CTFd admin panel, go to Admin → Beta Testers
2. Select a user from the dropdown list
3. Click "Add to Beta Testers"

### Removing Beta Testers

1. In the CTFd admin panel, go to Admin → Beta Testers
2. Find the user in the Beta Testers list
3. Click "Remove" next to their name

### Beta Tester Experience

- Beta testers can access and solve challenges before the CTF officially starts
- Beta testers cannot access any admin routes or features
- Beta testers appear as regular users to other participants

## How It Works

The plugin works by:
1. Promoting beta testers to admin role (giving them challenge access)
2. Tracking them in a separate BetaTesters table
3. Blocking their access to all admin routes
4. Automatically redirecting them to the challenges page if they try to access admin features

## Requirements

- CTFd v3.0.0 or higher

## License

This project is licensed under the GPLv3 License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request