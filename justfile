skill_src   := "skills/qgenda"
skill_dest  := env("HOME") / ".claude/skills/qgenda"
pkg_dir     := "dist/qgenda-skill"
pkg_version := `grep '^version' pyproject.toml | head -1 | sed 's/.*"\(.*\)"/\1/'`

# Show available recipes
default:
    @just --list

# Install Python dependencies with uv
deps:
    uv sync

# Run tests
test:
    uv run python -m pytest tests/ -v

# Install git hooks
hooks:
    cp git-hooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    @echo "Git hooks installed."

# Install skill globally (~/.claude/skills/qgenda/) — for non-plugin use
install:
    @echo "Installing QGenda skill globally..."
    mkdir -p {{ skill_dest }}/references {{ skill_dest }}/scripts
    cp {{ skill_src }}/SKILL.md {{ skill_dest }}/SKILL.md
    cp {{ skill_src }}/references/api-reference.md {{ skill_dest }}/references/api-reference.md
    # Dereference symlinks when copying scripts to the global install
    cp -L {{ skill_src }}/scripts/qgenda_query.py {{ skill_dest }}/scripts/qgenda_query.py
    cp -L {{ skill_src }}/scripts/qgenda_core.py {{ skill_dest }}/scripts/qgenda_core.py
    # Update script path in the installed SKILL.md to use absolute paths
    sed -i '' 's|scripts/qgenda_query.py|{{ skill_dest }}/scripts/qgenda_query.py|g' {{ skill_dest }}/SKILL.md
    @echo ""
    @echo "Installed to: {{ skill_dest }}/"
    @echo "The /qgenda skill is now available in all Claude Code projects."

# Remove globally installed skill
uninstall:
    rm -rf {{ skill_dest }}
    @echo "QGenda skill uninstalled."

# Package skill as a distributable tarball (for non-plugin distribution)
package:
    @echo "Packaging QGenda skill v{{ pkg_version }}..."
    rm -rf {{ pkg_dir }}
    mkdir -p {{ pkg_dir }}/references {{ pkg_dir }}/scripts
    cp {{ skill_src }}/SKILL.md              {{ pkg_dir }}/SKILL.md
    cp {{ skill_src }}/references/api-reference.md {{ pkg_dir }}/references/api-reference.md
    # Dereference symlinks when copying scripts into the package
    cp -L {{ skill_src }}/scripts/qgenda_query.py     {{ pkg_dir }}/scripts/qgenda_query.py
    cp -L {{ skill_src }}/scripts/qgenda_core.py      {{ pkg_dir }}/scripts/qgenda_core.py
    cp package/install.sh                          {{ pkg_dir }}/install.sh
    chmod +x {{ pkg_dir }}/install.sh
    cd dist && tar czf qgenda-skill-{{ pkg_version }}.tar.gz qgenda-skill/
    rm -rf {{ pkg_dir }}
    @echo ""
    @echo "Package created: dist/qgenda-skill-{{ pkg_version }}.tar.gz"
    @echo ""
    @echo "To install from the package:"
    @echo "  tar xzf dist/qgenda-skill-{{ pkg_version }}.tar.gz"
    @echo "  cd qgenda-skill && ./install.sh"
