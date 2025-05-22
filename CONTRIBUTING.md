# Contributing to bizCon

Thank you for your interest in contributing to bizCon! We welcome contributions from the community and are excited to collaborate with you.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (Python version, OS, etc.)
- Relevant error messages or logs

### Suggesting Features

We love new ideas! When suggesting a feature:
- Check if it's already been requested
- Explain the use case and benefit
- Provide examples if possible
- Consider implementation complexity

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**
   ```bash
   python test_framework.py
   pytest tests/
   ```
6. **Commit your changes**
   ```bash
   git commit -m "Add your descriptive commit message"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request**

## 🧪 Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Local Development
```bash
# Clone your fork
git clone https://github.com/your-username/bizcon.git
cd bizcon

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python test_framework.py
```

### Testing

We have several types of tests:

```bash
# Quick framework test (no API keys needed)
python test_framework.py

# Unit tests
pytest tests/unit/

# Integration tests  
pytest tests/integration/

# Test with real models (requires API keys)
python test_with_real_models.py
```

## 📝 Code Style

### Python Style Guide
- Follow PEP 8
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### Example:
```python
def evaluate_response(
    response: Dict[str, Any], 
    scenario: BusinessScenario,
    turn_index: int
) -> Dict[str, float]:
    """
    Evaluate a model response against scenario expectations.
    
    Args:
        response: The model's response dictionary
        scenario: Business scenario instance
        turn_index: Current conversation turn
        
    Returns:
        Dictionary with evaluation scores
    """
    # Implementation here
    pass
```

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove)
- Keep the first line under 50 characters
- Add detailed description if needed

Good examples:
- `Add support for custom evaluation weights`
- `Fix tool usage evaluation scoring bug`
- `Update documentation for scenario creation`

## 🏗️ Project Structure

### Adding New Scenarios

1. Create your scenario class in `scenarios/`
2. Inherit from `BusinessScenario`
3. Implement required methods
4. Add to scenario registry in `scenarios/__init__.py`
5. Add test cases

### Adding New Evaluators

1. Create evaluator in `evaluators/`
2. Inherit from `BaseEvaluator`
3. Implement the `evaluate()` method
4. Add to evaluator registry
5. Add comprehensive tests

### Adding New Tools

1. Create tool in `tools/`
2. Inherit from `BusinessTool`
3. Implement required methods
4. Add sample data if needed
5. Add to tools registry

### Adding New Model Providers

1. Create client in `models/`
2. Inherit from `ModelClient`
3. Implement all abstract methods
4. Add to provider registry
5. Update configuration examples

## 📚 Documentation

When contributing, please:
- Update relevant documentation
- Add docstrings to new functions/classes
- Update README if adding new features
- Add examples for new functionality

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Mock Tests**: Test without external dependencies

### Writing Good Tests

```python
def test_scenario_evaluation():
    """Test that scenario evaluation produces expected results."""
    # Arrange
    scenario = TestScenario()
    mock_response = {"content": "Test response"}
    
    # Act
    result = evaluate_scenario(scenario, mock_response)
    
    # Assert
    assert result["score"] >= 0
    assert result["score"] <= 10
    assert "explanation" in result
```

## 🎯 Areas We Need Help With

### High Priority
- [ ] Adding more business scenarios
- [ ] Improving evaluation accuracy
- [ ] Performance optimizations
- [ ] Documentation improvements

### Medium Priority
- [ ] Additional model provider integrations
- [ ] Advanced visualization features
- [ ] Industry-specific tool packs
- [ ] Multi-language support

### Good First Issues
- [ ] Fix typos in documentation
- [ ] Add more test cases
- [ ] Improve error messages
- [ ] Add configuration validation

## 🔄 Review Process

### Pull Request Guidelines

1. **Clear Description**: Explain what your PR does and why
2. **Reference Issues**: Link to related issues
3. **Test Coverage**: Include tests for new functionality
4. **Documentation**: Update docs as needed
5. **Small Changes**: Keep PRs focused and manageable

### Review Criteria

We review PRs based on:
- Code quality and style
- Test coverage
- Documentation completeness
- Performance impact
- Backward compatibility

## 🐛 Debugging Tips

### Common Issues

1. **Import Errors**: Check Python path setup
2. **API Errors**: Verify API keys are set
3. **Test Failures**: Run tests individually to isolate issues
4. **Performance Issues**: Use profiling tools

### Getting Help

- Open an issue for bugs or questions
- Join our discussions for feature ideas
- Check existing issues before creating new ones
- Provide minimal reproduction cases

## 📄 License

By contributing to bizCon, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors are recognized in:
- Repository contributor list
- Release notes for significant contributions
- README acknowledgments

## 👥 Project Authors

This project was created by:
- **[Akram Hasan Sharkar](https://github.com/ibnbd)** - Author & Lead Developer
- **[Maya Msahal](https://github.com/Mayamsah)** - Co-Author & Research Contributor

*Developed at [Olib AI](https://www.olib.ai)*

## 📖 Research & Citation

A research paper describing the bizCon framework will be published on arXiv.org. When citing this work, please reference both the software repository and the upcoming research paper.

Thank you for helping make bizCon better! 🚀