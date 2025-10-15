# 🤝 Contributing to EuroStyle Retail Demo Platform

Thank you for your interest in contributing to the EuroStyle Retail Demo Platform! This project aims to provide a realistic, production-quality multi-database demo system for the data engineering community.

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- **Data inconsistencies** between databases
- **Container startup issues**
- **Platform compatibility problems**
- **Documentation errors**

### ✨ Feature Requests  
- **New business scenarios** (e.g., B2B wholesale, returns processing)
- **Additional databases** (e.g., inventory management, CRM)
- **Integration examples** (dbt, Superset, Grafana)
- **Performance optimizations**

### 📚 Documentation
- **Tutorial improvements**
- **Use case examples**
- **Integration guides**
- **Translation** (currently English only)

### 🔧 Code Contributions
- **Data generation improvements**
- **New data patterns**
- **Query optimizations**
- **Platform compatibility**

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Git
- 4GB RAM, 5GB disk space

### Development Setup

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/demo_source_data_astoviq.git
cd demo_source_data_astoviq

# Set up development environment
chmod +x eurostyle.sh
./eurostyle.sh start

# Run the test suite
./eurostyle.sh demo-fast
./eurostyle.sh status

# Verify consistency checks pass
./scripts/utilities/validate_cross_system_consistency.py
```

## 📋 Development Guidelines

### Code Standards

#### Python Code
- **Style**: Follow PEP 8
- **Documentation**: Docstrings for all functions
- **Type hints**: Use where appropriate
- **Error handling**: Comprehensive exception handling

```python
def generate_customers(count: int, country_weights: Dict[str, float]) -> List[Dict]:
    """Generate realistic customer data with European focus.
    
    Args:
        count: Number of customers to generate
        country_weights: Distribution weights by country code
        
    Returns:
        List of customer dictionaries
        
    Raises:
        ValueError: If country_weights don't sum to 1.0
    """
```

#### Configuration Files
- **YAML format**: All configuration in YAML
- **Documentation**: Inline comments explaining options
- **Validation**: Schema validation where possible

### Data Quality Standards

#### Consistency Requirements
All contributions must maintain:
- ✅ **Revenue matching**: Operations = Finance = POS (exact match)
- ✅ **Foreign key integrity**: No orphaned records
- ✅ **Realistic patterns**: European business behaviors
- ✅ **Data validation**: Automated consistency checks

#### Testing Requirements
```bash
# All contributions must pass these tests
./eurostyle.sh demo-fast
python3 scripts/utilities/validate_cross_system_consistency.py
./scripts/utilities/test_documentation_commands.sh
```

### Architecture Principles

#### Configuration-Driven Development
- **No hard-coding**: All values in YAML configuration
- **Reusable components**: Generic scripts that work across databases
- **Template-based**: Use Jinja2 for code generation

#### Perfect Consistency
- **Cross-database validation**: Every change must maintain data integrity
- **Automated verification**: Built-in consistency checks
- **European compliance**: GDPR, VAT, multi-currency support

## 🔄 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow the coding standards above
- Add tests for new functionality
- Update documentation

### 3. Test Thoroughly
```bash
# Test your changes don't break existing functionality
./eurostyle.sh clean --force
./eurostyle.sh demo-full

# Verify consistency
python3 scripts/utilities/validate_cross_system_consistency.py

# Test documentation
./scripts/utilities/test_documentation_commands.sh --verbose
```

### 4. Update Documentation
Following WARP.md Rule #23, **all code changes require documentation updates**:

- **README.md**: If commands or workflows change
- **QUICKSTART.md**: If user-facing processes change  
- **Relevant docs/**: For technical changes
- **Configuration docs**: For any YAML changes

### 5. Submit Pull Request
- **Clear title**: Descriptive PR title
- **Detailed description**: What, why, and how
- **Test results**: Include test output
- **Breaking changes**: Clearly marked

## 🧪 Testing Guidelines

### Required Tests
Before submitting any PR:

```bash
# 1. Clean environment test
./eurostyle.sh clean --force
./eurostyle.sh start
./eurostyle.sh demo-fast

# 2. Consistency validation
python3 scripts/utilities/validate_cross_system_consistency.py

# 3. Documentation validation  
./scripts/utilities/validate_documentation.sh --verbose
./scripts/utilities/test_documentation_commands.sh --verbose

# 4. Full-scale test (for major changes)
./eurostyle.sh clean --force
./eurostyle.sh demo-full
```

### Performance Tests
For data generation changes:

```bash
# Benchmark data generation performance
time python3 scripts/data-generation/universal_data_generator_v2.py --all --mode demo
time python3 scripts/data-generation/universal_data_generator_v2.py --all --mode full

# Memory usage validation
docker stats eurostyle_clickhouse_retail
```

## 📊 Contribution Ideas

### 🎯 High-Impact Contributions

#### New Business Scenarios
- **Returns processing**: Customer returns and refunds
- **B2B wholesale**: Business-to-business transactions
- **Loyalty programs**: Advanced customer rewards
- **Subscription services**: Recurring revenue models

#### Integration Examples
- **dbt transformations**: Complete dbt project
- **Superset dashboards**: Pre-built business dashboards
- **Grafana monitoring**: System health monitoring
- **Apache Airflow**: Data pipeline orchestration

#### Data Engineering Features
- **CDC simulation**: Change data capture patterns
- **Data lake integration**: Parquet export capabilities
- **Stream processing**: Kafka integration examples
- **ML feature stores**: Feature engineering examples

### 🔧 Technical Improvements

#### Performance Optimizations
- **Query optimization**: Faster ClickHouse queries
- **Data compression**: Better storage efficiency
- **Memory usage**: Reduced resource requirements
- **Startup time**: Faster container initialization

#### Platform Support
- **ARM64 support**: Apple Silicon compatibility
- **Windows support**: Windows container support
- **Cloud deployment**: AWS/GCP/Azure examples
- **Kubernetes**: K8s deployment manifests

## 💡 Feature Request Template

When suggesting new features, please include:

```markdown
### Feature Description
Clear description of the proposed feature

### Business Value
Why this feature would be valuable for demo users

### Implementation Approach
High-level technical approach

### Data Consistency Impact
How this maintains/enhances cross-database consistency

### Testing Strategy
How to verify the feature works correctly

### Documentation Requirements
What documentation needs to be created/updated
```

## 🐛 Bug Report Template

```markdown
### Bug Description
Clear description of the issue

### Environment
- OS: (macOS/Linux/Windows)
- Docker version:
- Python version:
- Available RAM:

### Steps to Reproduce
1. Command/action taken
2. Expected result
3. Actual result

### Logs
Relevant log output or error messages

### Consistency Check Results
Output from: `python3 scripts/utilities/validate_cross_system_consistency.py`
```

## 🎉 Recognition

Contributors will be recognized in:
- **README.md contributors section**
- **Release notes** for significant contributions
- **Documentation credits**
- **Community shout-outs** on social media

## 📞 Getting Help

### Community Support
- **GitHub Issues**: Technical questions and bugs
- **GitHub Discussions**: General questions and ideas
- **Pull Request Reviews**: Code feedback and guidance

### Development Questions
For complex development questions, please:
1. Check existing issues and discussions
2. Review the WARP.md development rules
3. Look at similar implementations in the codebase
4. Create a detailed issue with context

## 📜 Code of Conduct

### Our Standards
- **Respectful communication**: Professional and constructive feedback
- **Inclusive environment**: Welcome contributors of all backgrounds
- **Collaborative approach**: Help others learn and grow
- **Quality focus**: Maintain high standards for demo quality

### Unacceptable Behavior
- Harassment or discrimination
- Spam or off-topic content  
- Disruptive behavior
- Violation of platform terms

---

## 🚀 Ready to Contribute?

1. **⭐ Star the repository** to show your support
2. **🍴 Fork the project** to your GitHub account
3. **📝 Pick an issue** or create a feature request
4. **💻 Start coding** following these guidelines
5. **📤 Submit your PR** with thorough testing

**Thank you for helping make the EuroStyle Retail Demo Platform better for the entire data engineering community!** 🎉

---

*For questions about these guidelines, please create an issue with the `documentation` label.*