# Contributing to FB Manager

Thank you for your interest in contributing to FB Manager!

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/fbmanager.git
cd fbmanager
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your test credentials
```

### 5. Run Tests

```bash
python main.py
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused

## Submitting Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test thoroughly
4. Commit with clear messages: `git commit -m "Add feature: description"`
5. Push to your fork: `git push origin feature/your-feature-name`
6. Create a Pull Request

## Reporting Issues

When reporting issues, please include:

- Operating System and version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

## Code of Conduct

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community

## Questions?

Open an issue or reach out to the maintainers.

Thank you for contributing! 🎉
