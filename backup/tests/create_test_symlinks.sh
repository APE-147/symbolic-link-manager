#!/bin/bash
# Script to create test symlinks for TUI scrolling verification

# Create test directory structure
TEST_DIR="/tmp/symlink_test_$(date +%s)"
mkdir -p "$TEST_DIR/project-alpha"
mkdir -p "$TEST_DIR/project-beta"
mkdir -p "$TEST_DIR/project-gamma"
mkdir -p "$TEST_DIR/targets"
mkdir -p "$TEST_DIR/unclassified"

echo "Creating test symlinks in: $TEST_DIR"

# Create some target files
for i in {1..60}; do
    echo "Target file $i" > "$TEST_DIR/targets/target-$i.txt"
done

# Create symlinks for project-alpha (20 links)
for i in {1..20}; do
    ln -sf "$TEST_DIR/targets/target-$i.txt" "$TEST_DIR/project-alpha/link-alpha-$i"
done

# Create symlinks for project-beta (15 links)
for i in {21..35}; do
    ln -sf "$TEST_DIR/targets/target-$i.txt" "$TEST_DIR/project-beta/link-beta-$i"
done

# Create symlinks for project-gamma (10 links)
for i in {36..45}; do
    ln -sf "$TEST_DIR/targets/target-$i.txt" "$TEST_DIR/project-gamma/link-gamma-$i"
done

# Create unclassified symlinks (15 links)
for i in {46..60}; do
    ln -sf "$TEST_DIR/targets/target-$i.txt" "$TEST_DIR/unclassified/link-unclassified-$i"
done

# Create a few broken symlinks for testing
ln -sf "$TEST_DIR/targets/nonexistent-1.txt" "$TEST_DIR/project-alpha/broken-link-1"
ln -sf "$TEST_DIR/targets/nonexistent-2.txt" "$TEST_DIR/project-beta/broken-link-2"
ln -sf "$TEST_DIR/targets/nonexistent-3.txt" "$TEST_DIR/unclassified/broken-link-3"

echo "Test environment created!"
echo ""
echo "Total symlinks created: 63 (60 valid + 3 broken)"
echo "  - project-alpha: 21 symlinks (20 valid + 1 broken)"
echo "  - project-beta: 16 symlinks (15 valid + 1 broken)"
echo "  - project-gamma: 10 symlinks (all valid)"
echo "  - unclassified: 16 symlinks (15 valid + 1 broken)"
echo ""
echo "To test the TUI with scrolling, run:"
echo "  lk --target \"$TEST_DIR\""
echo ""
echo "To clean up when done:"
echo "  rm -rf \"$TEST_DIR\""
echo ""
echo "Test directory: $TEST_DIR"
