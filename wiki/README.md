# bizCon Wiki Documentation

This directory contains comprehensive documentation for the bizCon framework as GitHub Wiki pages.

## 📁 Wiki Structure

```
wiki/
├── Home.md                    # Main landing page
├── Getting-Started.md         # Installation and quick start guide
├── Architecture.md            # Framework architecture overview
├── Business-Scenarios.md      # All 8 business scenarios documentation
├── Business-Tools.md          # All 8 business tools documentation
├── Evaluation-System.md       # Evaluation dimensions and scoring
├── Configuration.md           # Configuration file reference
├── Advanced-Features.md       # Dashboard and visualization features
├── Testing-Guide.md           # Testing strategies and mock models
├── API-Reference.md           # Complete API documentation
├── FAQ.md                     # Frequently asked questions
├── _Sidebar.md               # Navigation sidebar for GitHub Wiki
└── README.md                 # This file
```

## 🚀 Using the Wiki

### GitHub Wiki Setup

1. **Enable Wiki** in your GitHub repository settings
2. **Clone the wiki repository**:
   ```bash
   git clone https://github.com/yourusername/bizcon.wiki.git
   ```
3. **Copy all files** from this `wiki/` directory to the cloned wiki repository
4. **Commit and push**:
   ```bash
   cd bizcon.wiki
   git add .
   git commit -m "Add comprehensive wiki documentation"
   git push
   ```

### Local Preview

To preview the wiki locally:

1. Install a markdown preview tool:
   ```bash
   npm install -g markdown-preview
   ```

2. Preview any page:
   ```bash
   markdown-preview Home.md
   ```

## 📝 Wiki Pages Overview

### Core Documentation
- **[Home](Home.md)** - Main landing page with project overview
- **[Getting Started](Getting-Started.md)** - Installation, setup, and first evaluation
- **[Architecture](Architecture.md)** - Technical architecture and design patterns

### Component Documentation
- **[Business Scenarios](Business-Scenarios.md)** - Detailed documentation of all 8 scenarios
- **[Business Tools](Business-Tools.md)** - Mock business tools and their APIs
- **[Evaluation System](Evaluation-System.md)** - Scoring methodology and evaluators

### Configuration & Usage
- **[Configuration](Configuration.md)** - YAML configuration reference
- **[Advanced Features](Advanced-Features.md)** - Dashboards, analytics, and visualizations
- **[Testing Guide](Testing-Guide.md)** - Testing strategies and CI/CD

### Reference
- **[API Reference](API-Reference.md)** - Complete code API documentation
- **[FAQ](FAQ.md)** - Common questions and troubleshooting

## 🔗 Navigation

The **[_Sidebar.md](_Sidebar.md)** file provides the navigation structure for GitHub Wiki. It includes:
- Hierarchical organization of all pages
- Quick links to major sections
- External links to repository resources

## 🎨 Formatting Guidelines

The wiki uses GitHub Flavored Markdown with:
- **Mermaid diagrams** for architecture visualization
- **Code blocks** with syntax highlighting
- **Tables** for structured data
- **Emoji** for visual enhancement
- **Internal links** using `[Text](Page-Name)` format

## 🔄 Keeping Wiki Updated

When updating the framework:
1. Update relevant wiki pages
2. Test all internal links
3. Update the sidebar if adding new pages
4. Commit changes to both main repo and wiki

## 📚 Additional Resources

- [GitHub Wiki Documentation](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
- [Markdown Guide](https://www.markdownguide.org/)
- [Mermaid Diagram Syntax](https://mermaid-js.github.io/mermaid/)

---

**Note**: This wiki documentation is designed to be comprehensive and self-contained. Each page can be read independently while maintaining cohesive navigation through the sidebar.