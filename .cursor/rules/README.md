# Cursor Rules for Maître Joueur

This directory contains Cursor rules for the Maître Joueur RPG Session Management Tool. These rules provide guidance to the Cursor AI assistant on various aspects of the project.

## Rules Structure

- **general.mdc**: Main rules for package management, code style, and security
- **workflow.mdc**: Development workflow guidelines and error handling
- **implementation.mdc**: Technical implementation guidelines for specific features
- **project_structure.mdc**: Project structure overview and documentation standards
- **code_tasks.mdc**: Guidelines for code implementation and task handling

## Reference Documents
- **PROJECT_STRUCTURE.md**: Detailed project structure documentation
- **FINAL_SUMMARY.md**: Project summary and status
- **COMPRESSION_FEATURE.md**: Documentation for compression features
- **LARGE_FILE_FIXES.md**: Documentation for large file handling improvements

## Usage

Cursor automatically includes these rules when you interact with the AI assistant. Rules with `alwaysApply: true` are always included, while others are contextually applied based on the files you're working with.

To reference a specific rule in a conversation, use the @ symbol followed by the rule name (without the extension), e.g., `@code_tasks`. 