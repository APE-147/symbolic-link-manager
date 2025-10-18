#!/usr/bin/env python3
"""Quick test to verify hash detection is working on real Dropbox hashes."""

from symlink_manager.core.scanner import _is_hash_like_name

# Real Dropbox hashes from user's output
test_hashes = [
    "1R3_9ZoEWvefI4rTylIiU",
    "6UA9a6LZnqYXSA8WzC-ZV",
    "tv5NqM2yTK-Aik4TtsKhy",
    "pzl5hFDLa-32dKP6a8g4U",
    "4ST9V50OiHPY6-3rJf-ui",
    "vXl-51VXN9oL4BHwxOC5Q",
    "Drj342tLwOyOwhj9--HVA",
    "40LzdGD4hWt7iHxo1oQzR",
    "iUvBobAubJTesUfDTxjnm",
    "ebm4FRwMjKFxacDzB2xZ2",
]

# Normal names that should NOT be detected
normal_names = [
    "my-project-data",
    "video-downloader",
    "custom",
    "rss-inbox-data",
    "MediaCrawler",
    "build-depends.sh",
]

print("Testing Dropbox hash detection:")
print("=" * 60)

all_passed = True

print("\nDropbox hashes (should be detected as TRUE):")
for name in test_hashes:
    result = _is_hash_like_name(name)
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"  {name:30s} → {result:5} {status}")
    if not result:
        all_passed = False

print("\nNormal names (should be detected as FALSE):")
for name in normal_names:
    result = _is_hash_like_name(name)
    status = "✅ PASS" if not result else "❌ FAIL"
    print(f"  {name:30s} → {result:5} {status}")
    if result:
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("✅ All tests PASSED! Hash detection is working correctly.")
else:
    print("❌ Some tests FAILED! Hash detection needs fixing.")
    exit(1)
