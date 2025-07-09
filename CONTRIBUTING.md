# Contributing to Quant Commander

We welcome contributions to Quant Commander! This document provides guidelines for contributing to the project.

## 🎯 **Ways to Contribute**

### **Bug Reports**
- Use the [GitHub Issues](https://github.com/yourusername/quantcommander/issues) page
- Include detailed reproduction steps
- Provide system information (OS, Python version, dependencies)
- Include error logs and screenshots if applicable

### **Feature Requests**
- Open a [GitHub Discussion](https://github.com/yourusername/quantcommander/discussions)
- Describe the use case and expected behavior
- Explain how it benefits the financial analysis workflow
- Consider implementation complexity and maintenance

### **Code Contributions**
- Fork the repository
- Create a feature branch from `develop`
- Follow the coding standards below
- Add tests for new functionality
- Update documentation as needed
- Submit a pull request

## 🛠️ **Development Setup**

### **Prerequisites**
- Python 3.8+
- Git
- Ollama with Gemma3 model
- Virtual environment (recommended)

### **Setup Instructions**
```bash
# 1. Fork and clone the repository
git clone https://github.com/yourusername/quantcommander.git
cd quantcommander

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install -r requirements-dev.txt

# 5. Setup pre-commit hooks
pre-commit install

# 6. Run tests to verify setup
python -m pytest tests/
```

## 📝 **Coding Standards**

### **Python Code**
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Include comprehensive docstrings for all functions and classes
- Maximum line length: 100 characters
- Use meaningful variable and function names

### **Code Example**
```python
def analyze_financial_data(
    df: pd.DataFrame, 
    analysis_type: str = "contribution"
) -> Tuple[str, Dict[str, Any]]:
    """
    Analyze financial data based on specified analysis type.
    
    Args:
        df: Input DataFrame with financial data
        analysis_type: Type of analysis ('contribution', 'variance', etc.)
        
    Returns:
        Tuple of (analysis_result, metadata)
        
    Raises:
        ValueError: If analysis_type is not supported
    """
    # Implementation here
    pass
```

### **Documentation**
- Use Markdown for documentation files
- Include code examples in documentation
- Update README.md for significant changes
- Add inline comments for complex logic

### **Testing**
- Write unit tests for all new functions
- Include integration tests for major features
- Maintain test coverage above 80%
- Use descriptive test names

## 🧪 **Testing Guidelines**

### **Running Tests**
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_contribution_analysis.py

# Run with coverage
python -m pytest --cov=. tests/

# Run integration tests
python -m pytest tests/integration/
```

### **Test Structure**
```python
def test_contribution_analysis_basic():
    """Test basic contribution analysis functionality."""
    # Arrange
    df = create_test_dataframe()
    analyzer = ContributionAnalyzer()
    
    # Act
    result = analyzer.perform_analysis(df)
    
    # Assert
    assert result is not None
    assert "top_contributor" in result
    assert result["total_categories"] > 0
```

## 📋 **Pull Request Process**

### **Before Submitting**
1. **Run Tests**: Ensure all tests pass
2. **Code Quality**: Run linting and formatting tools
3. **Documentation**: Update relevant documentation
4. **Commit Messages**: Use clear, descriptive commit messages

### **Commit Message Format**
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(analysis): add budget quantitative analysis feature

fix(chat): resolve issue with timescale analysis repetition

docs(readme): update installation instructions
```

### **Pull Request Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] All existing tests pass
- [ ] New tests added for changes
- [ ] Manual testing completed

## Documentation
- [ ] Documentation updated
- [ ] Code comments added
- [ ] API documentation updated (if applicable)

## Additional Notes
Any additional context or notes for reviewers
```

## 🔍 **Code Review Process**

### **Review Criteria**
- **Functionality**: Does the code work as intended?
- **Testing**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Performance**: Are there any performance concerns?
- **Security**: Are there any security implications?
- **Maintainability**: Is the code easy to understand and maintain?

### **Review Timeline**
- Initial review within 2-3 business days
- Follow-up reviews within 1 business day
- Merge after approval from at least one maintainer

## 🏷️ **Release Process**

### **Version Numbering**
We use Semantic Versioning (SemVer):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### **Release Checklist**
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number updated
- [ ] Changelog updated
- [ ] GitHub release created
- [ ] Docker images updated (if applicable)

## 🤝 **Community Guidelines**

### **Code of Conduct**
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Acknowledge different perspectives and experiences

### **Communication**
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code review and technical discussion

### **Getting Help**
- Check existing issues and discussions first
- Provide context and details when asking questions
- Be patient and respectful when seeking help
- Help others when you can

## 📈 **Areas for Contribution**

### **High Priority**
- Performance optimizations for large datasets
- Additional LLM integrations (Claude, GPT-4, etc.)
- Enhanced data visualization options
- Mobile-responsive UI improvements

### **Medium Priority**
- Additional financial analysis types
- Export functionality (PDF reports, etc.)
- Caching and session management
- Internationalization support

### **Low Priority**
- Theme customization
- Plugin system for custom analysis
- Advanced dashboard features
- Integration with external data sources

## 🎉 **Recognition**

Contributors will be:
- Listed in the project's contributors section
- Mentioned in release notes for significant contributions
- Invited to join the project's maintainer team (for consistent contributors)

## 📞 **Contact**

- **Project Maintainers**: Listed in [MAINTAINERS.md](MAINTAINERS.md)
- **General Questions**: [GitHub Discussions](https://github.com/yourusername/quantcommander/discussions)
- **Security Issues**: Please email security@quantcommander.com

---

Thank you for contributing to Quant Commander! Your efforts help make financial data analysis more accessible and powerful for everyone. 🚀
