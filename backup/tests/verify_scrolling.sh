#!/bin/bash
# Automated verification script for TUI scrolling and adaptive width

set -e

echo "=========================================="
echo "TUI Scrolling & Adaptive Width Verification"
echo "=========================================="
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}[1/6] Checking prerequisites...${NC}"
if ! command -v lk &> /dev/null; then
    echo -e "${RED}✗ 'lk' command not found. Please run: pip install -e .${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 'lk' command found${NC}"

if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}⚠ 'pytest' not found. Skipping unit tests.${NC}"
else
    echo -e "${GREEN}✓ 'pytest' found${NC}"
fi
echo

# Run unit tests
echo -e "${BLUE}[2/6] Running unit tests...${NC}"
if command -v pytest &> /dev/null; then
    if pytest tests/ -v --tb=short; then
        echo -e "${GREEN}✓ All unit tests pass${NC}"
    else
        echo -e "${RED}✗ Some unit tests failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Skipping unit tests (pytest not installed)${NC}"
fi
echo

# Create test symlinks
echo -e "${BLUE}[3/6] Creating test environment...${NC}"
if [ -x "./tests/create_test_symlinks.sh" ]; then
    TEST_DIR=$(./tests/create_test_symlinks.sh | grep "Test directory:" | cut -d' ' -f3)
    echo -e "${GREEN}✓ Test environment created: $TEST_DIR${NC}"
else
    echo -e "${RED}✗ create_test_symlinks.sh not found or not executable${NC}"
    exit 1
fi
echo

# Verify test environment
echo -e "${BLUE}[4/6] Verifying test environment...${NC}"
SYMLINK_COUNT=$(find "$TEST_DIR" -type l | wc -l | tr -d ' ')
echo "  - Total symlinks: $SYMLINK_COUNT"
if [ "$SYMLINK_COUNT" -ge 60 ]; then
    echo -e "${GREEN}✓ Test environment has sufficient symlinks ($SYMLINK_COUNT >= 60)${NC}"
else
    echo -e "${YELLOW}⚠ Test environment has only $SYMLINK_COUNT symlinks (expected >= 60)${NC}"
fi
echo

# Test terminal width detection
echo -e "${BLUE}[5/6] Testing terminal width detection...${NC}"
TERM_COLS=$(tput cols 2>/dev/null || echo "unknown")
TERM_LINES=$(tput lines 2>/dev/null || echo "unknown")
echo "  - Current terminal: ${TERM_COLS} cols × ${TERM_LINES} lines"

if [ "$TERM_COLS" != "unknown" ] && [ "$TERM_COLS" -lt 60 ]; then
    echo -e "${YELLOW}⚠ Terminal width is narrow ($TERM_COLS cols). Minimum 60 recommended.${NC}"
elif [ "$TERM_COLS" != "unknown" ]; then
    echo -e "${GREEN}✓ Terminal width is suitable ($TERM_COLS cols)${NC}"
fi

if [ "$TERM_LINES" != "unknown" ] && [ "$TERM_LINES" -lt 24 ]; then
    echo -e "${YELLOW}⚠ Terminal height is short ($TERM_LINES lines). Minimum 24 recommended.${NC}"
elif [ "$TERM_LINES" != "unknown" ]; then
    echo -e "${GREEN}✓ Terminal height is suitable ($TERM_LINES lines)${NC}"
fi
echo

# Provide manual testing instructions
echo -e "${BLUE}[6/6] Manual testing instructions${NC}"
echo "=========================================="
echo
echo -e "${GREEN}The test environment is ready!${NC}"
echo
echo "To test TUI scrolling and adaptive width, run:"
echo
echo -e "  ${YELLOW}lk --target \"$TEST_DIR\"${NC}"
echo
echo "Test checklist:"
echo "  [ ] Scroll indicators appear when navigating"
echo "  [ ] Arrow keys (↑/↓) or j/k scroll smoothly"
echo "  [ ] Cursor stays centered in viewport"
echo "  [ ] Group headers visible with their items"
echo "  [ ] \"↑ N more above\" shows correct count"
echo "  [ ] \"↓ N more below\" shows correct count"
echo "  [ ] Columns adapt to terminal width"
echo "  [ ] Long names/paths truncated with \"…\""
echo "  [ ] Enter key shows full details"
echo "  [ ] q/Esc quits properly"
echo
echo "To test different terminal widths:"
echo "  1. Resize terminal to narrow (80 cols)"
echo "  2. Relaunch: lk --target \"$TEST_DIR\""
echo "  3. Verify columns adapt and text truncates"
echo "  4. Repeat for wide terminal (160+ cols)"
echo
echo "When done testing, clean up with:"
echo -e "  ${YELLOW}rm -rf \"$TEST_DIR\"${NC}"
echo
echo "=========================================="
echo -e "${GREEN}Verification complete!${NC}"
echo "=========================================="
