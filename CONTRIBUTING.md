# Contributing to TSX Supersite GAMMA Processing

Thank you for considering contributing to this project! This document provides guidelines for contributing.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check if the issue already exists in the [issue tracker](https://github.com/eliot-eaton/TSX_supersite_GAMMA_processing/issues)
2. If not, create a new issue with:
   - Clear description of the problem
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version, GAMMA version)

### Submitting Changes

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages:
   ```bash
   git commit -m "Add feature: description of feature"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to functions and classes
- Comment complex logic
- Keep functions focused and small

### Testing

- Test your changes with real or simulated data
- Verify scripts run without errors
- Check that help messages are clear and accurate
- Test edge cases and error handling

### Documentation

- Update README.md if adding new features
- Add docstrings to new functions
- Update WORKFLOW.md if changing the process
- Include examples in help text

## Areas for Contribution

### Priority Areas

1. **Enhanced Error Handling**
   - Better error messages
   - Graceful failure handling
   - Input validation

2. **EOC API Integration**
   - Implement actual EOC Geoservice API calls
   - Add authentication handling
   - Progress tracking for downloads

3. **GAMMA Command Integration**
   - Fill in actual GAMMA command calls
   - Add parameter validation
   - Improve error checking

4. **Testing**
   - Unit tests for utility functions
   - Integration tests for workflows
   - Test data generation

5. **Documentation**
   - More examples
   - Tutorial notebooks
   - Video tutorials

### Other Contributions

- Bug fixes
- Performance improvements
- Additional features
- Better logging
- Configuration validation
- GUI tools

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/eliot-eaton/TSX_supersite_GAMMA_processing.git
cd TSX_supersite_GAMMA_processing
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
pip install -r requirements.txt
```

4. Make your changes and test

## Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Include tests if applicable
- Update documentation
- Reference related issues
- Ensure code passes syntax checks
- Add yourself to contributors if desired

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards other contributors

## Questions?

If you have questions:
- Open an issue for discussion
- Tag it with "question"
- Be specific about what you need help with

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

Contributors are acknowledged in the README.md file.

Thank you for contributing to TSX Supersite GAMMA Processing!
