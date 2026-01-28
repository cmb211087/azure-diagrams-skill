# Contributing to Azure Diagrams Skill

First off, thank you for considering contributing! This skill is used by developers and architects worldwide, and your contributions help make it better for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

**When reporting a bug, include:**
- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots of diagram output (if applicable)
- The prompt you used
- Your environment (GitHub Copilot, Claude Code, VS Code)

### Suggesting Enhancements

**Great enhancement ideas include:**
- New Azure architecture patterns
- Additional diagram types
- Better documentation or examples
- New IaC parsing capabilities (e.g., Pulumi support)
- Improved styling or layout fixes

### Contributing Code

1. **Fork the repository**
2. **Create a branch** for your feature: `git checkout -b feature/amazing-pattern`
3. **Make your changes**
4. **Test your changes** - generate diagrams and verify they render correctly
5. **Submit a pull request**

## What We're Looking For

### High-Priority Contributions

- **New architecture patterns** in `references/common-patterns.md`
- **Additional IaC examples** (Pulumi, Ansible, etc.)
- **Bug fixes** for diagram rendering issues
- **Documentation improvements**

### Code Style

For Python diagram code:
- Use descriptive variable names for resources
- Group related resources in clusters
- Add comments explaining complex layouts
- Follow existing patterns in `references/`

Example:
```python
# Good - descriptive and organized
with Cluster("Data Tier"):
    primary_db = SQLDatabases("Primary\nSQL Database")
    cache = CacheForRedis("Session\nCache")

# Less good - unclear
with Cluster("stuff"):
    x = SQLDatabases("db")
    y = CacheForRedis("cache")
```

### Documentation Style

- Use clear, concise language
- Include code examples that can be copy-pasted
- Add screenshots for visual examples
- Keep the target audience in mind (Azure architects, developers)

## Adding a New Architecture Pattern

1. Add the pattern to `references/common-patterns.md`
2. Include:
   - Pattern name and description
   - Complete, working Python code
   - Key Azure services used
   - When to use this pattern
3. Test the diagram renders correctly
4. Optionally add an example image to `examples/`

## Adding IaC Support

To add support for a new IaC format:

1. Add parsing guidance to `references/iac-to-diagram.md`
2. Include:
   - Resource type mapping table
   - Example prompts
   - Sample IaC file
   - Generated diagram example
3. Document any limitations

## Pull Request Process

1. Update documentation if needed
2. Add yourself to the contributors list (optional)
3. Ensure your PR description clearly explains the change
4. Link any related issues

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
