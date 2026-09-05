#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# GEO-CN 国内版 GEO 审计工具卸载脚本
# 作者：simonsxxs（一个不会代码的AI极客）  微信交流群：simonsxxs
# ============================================================

CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_DIR}/skills"
AGENTS_DIR="${CLAUDE_DIR}/agents"

# Detect if running via curl pipe (no interactive input available)
INTERACTIVE=true
if [ ! -t 0 ]; then
    INTERACTIVE=false
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ensure unmatched globs expand to nothing
shopt -s nullglob

echo ""
echo -e "${YELLOW}GEO-CN 国内版 GEO 审计工具卸载程序${NC}"
echo ""
echo "以下内容将被删除："
echo ""

# List what will be removed
[ -d "$SKILLS_DIR/geo" ] && echo "  → ${SKILLS_DIR}/geo/"
for skill_dir in "$SKILLS_DIR"/geo-*/; do
    [ -d "$skill_dir" ] && echo "  → ${skill_dir}"
done
for agent_file in "$AGENTS_DIR"/geo-*.md; do
    [ -f "$agent_file" ] && echo "  → ${agent_file}"
done

echo ""
if [ "$INTERACTIVE" = true ]; then
    read -p "Are you sure you want to uninstall? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Uninstall cancelled."
        exit 0
    fi
else
    echo -e "${YELLOW}Non-interactive mode — proceeding with uninstall...${NC}"
fi

echo ""

# Remove main skill
if [ -d "$SKILLS_DIR/geo" ]; then
    rm -rf "$SKILLS_DIR/geo"
    echo -e "${GREEN}✓ Removed main skill${NC}"
fi

# Remove sub-skills
for skill_dir in "$SKILLS_DIR"/geo-*/; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        rm -rf "$skill_dir"
        echo -e "${GREEN}✓ Removed ${skill_name}${NC}"
    fi
done

# Remove agents
for agent_file in "$AGENTS_DIR"/geo-*.md; do
    if [ -f "$agent_file" ]; then
        agent_name=$(basename "$agent_file")
        rm -f "$agent_file"
        echo -e "${GREEN}✓ Removed ${agent_name}${NC}"
    fi
done

echo ""
echo -e "${GREEN}GEO-CN 工具已卸载完成。${NC}"
echo ""
echo "说明：Python 依赖安装在工具目录内的独立虚拟环境中，"
echo "已随目录一并删除，不会影响你系统里的 Python。"
echo ""
echo "说明：~/.geo-prospects/ 下的客户数据未删除。"
echo "如需手动删除："
echo "  rm -rf ~/.geo-prospects"
echo ""
